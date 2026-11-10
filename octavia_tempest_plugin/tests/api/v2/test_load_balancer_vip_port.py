#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

from concurrent import futures
import json
import threading

from oslo_log import log as logging
from tempest import config
from tempest.lib.common.utils import data_utils
from tempest.lib.common.utils import test_utils
from tempest.lib import decorators
from tempest.lib import exceptions

from octavia_tempest_plugin.common import constants as const
from octavia_tempest_plugin.tests import test_base
from octavia_tempest_plugin.tests import waiters

CONF = config.CONF
LOG = logging.getLogger(__name__)

# Neutron port attributes
ALLOWED_ADDRESS_PAIRS = 'allowed_address_pairs'
BINDING_HOST_ID = 'binding:host_id'
DEVICE_ID = 'device_id'
DEVICE_OWNER = 'device_owner'
FIXED_IPS = 'fixed_ips'
IP_ADDRESS = 'ip_address'
NETWORK_ID = 'network_id'
REVISION_NUMBER = 'revision_number'

DEFAULT_POOL = 'default_pool'
# device_owner of a VIP port claimed by the F5 provider
F5_VIP_PORT_DEVICE_OWNER = 'network:f5listener'
# Key of the host list in the availability zone data of the F5 provider
HOSTS = 'hosts'


class LoadBalancerVipPortAPITest(test_base.LoadBalancerBaseTest):
    """Load balancers on a VIP port created by the user (vip_port_id).

    The provider claims such a port while its load balancer exists and hands
    it back to the project when the load balancer is deleted
    (octavia-issues#66):

    * claimed: device_owner network:f5listener, device_id <load balancer>,
      binding:host_id <host the load balancer is scheduled to>
    * a further load balancer on the port is refused
    * released: device_owner, device_id, binding:host_id and
      allowed_address_pairs are cleared, the port itself is kept

    The F5 provider implements this, so the tests run only for it.
    """

    @classmethod
    def skip_checks(cls):
        super(LoadBalancerVipPortAPITest, cls).skip_checks()
        if CONF.load_balancer.provider not in const.F5_PROVIDERS:
            raise cls.skipException(
                'Only the F5 provider claims VIP ports, provider is '
                '{}.'.format(CONF.load_balancer.provider))
        if CONF.load_balancer.test_with_noop:
            raise cls.skipException('The no-op drivers do not claim ports.')

    @classmethod
    def setup_clients(cls):
        """Setup client aliases."""
        super(LoadBalancerVipPortAPITest, cls).setup_clients()
        # Cloud admin: every attribute of every port, amphora (host) records
        # and availability zone profiles
        cls.admin_ports_client = cls.os_admin.ports_client
        cls.admin_amphora_client = (
            cls.os_admin.load_balancer_v2.AmphoraClient())
        cls.admin_az_client = (
            cls.os_admin.load_balancer_v2.AvailabilityZoneClient())
        cls.admin_az_profile_client = (
            cls.os_admin.load_balancer_v2.AvailabilityZoneProfileClient())

    @classmethod
    def resource_setup(cls):
        """Setup resources needed by the tests."""
        super(LoadBalancerVipPortAPITest, cls).resource_setup()

        # A load balancer for the tests that leave its port alone
        cls.shared_port = cls._create_vip_port(cls.addClassResourceCleanup)
        cls.shared_lb = cls._create_lb_on_port(
            cls.addClassResourceCleanup, cls.shared_port[const.ID], 'shared')

    @classmethod
    def _create_vip_port(cls, add_cleanup):
        """Create a port in the VIP subnet, like a user would.

        :param add_cleanup: addCleanup or addClassResourceCleanup
        """
        port_kwargs = {const.NAME: data_utils.rand_name('lb_member_vip_port'),
                       NETWORK_ID: cls.lb_member_vip_net[const.ID]}
        if cls.lb_member_vip_subnet:
            port_kwargs[FIXED_IPS] = [
                {const.SUBNET_ID: cls.lb_member_vip_subnet[const.ID]}]
        port = cls.lb_mem_ports_client.create_port(**port_kwargs)['port']
        # Registered before the load balancers on the port, so it runs after
        # their cleanups
        add_cleanup(cls._delete_vip_port, port[const.ID])
        return port

    @classmethod
    def _delete_vip_port(cls, port_id):
        """Delete a VIP port, unless a load balancer still uses it.

        Deleting the port would break the load balancer. If the load balancer
        could not be deleted, both are left to the cleanup after the run.
        """
        lbs = cls.mem_lb_client.list_loadbalancers(
            query_params='{}={}'.format(const.VIP_PORT_ID, port_id))
        in_use = [lb[const.ID] for lb in lbs
                  if lb[const.PROVISIONING_STATUS] != const.DELETED]
        if in_use:
            LOG.error('Not deleting VIP port %s, load balancer %s uses it.',
                      port_id, ', '.join(in_use))
            return
        # As admin: if the release failed, the project cannot delete it
        test_utils.call_and_ignore_notfound_exc(
            cls.admin_ports_client.delete_port, port_id)

    @classmethod
    def _create_lb_on_port(cls, add_cleanup, port_id, name, wait=True,
                           **kwargs):
        """Create a load balancer with vip_port_id.

        :param add_cleanup: addCleanup or addClassResourceCleanup
        :param name: Part of the load balancer name.
        :param wait: Wait until the load balancer is ACTIVE.
        :param kwargs: More load balancer attributes.
        """
        lb_kwargs = cls._lb_kwargs(port_id, name)
        lb_kwargs.update(kwargs)
        lb = cls.mem_lb_client.create_loadbalancer(**lb_kwargs)
        add_cleanup(cls.mem_lb_client.cleanup_loadbalancer, lb[const.ID])
        if wait:
            lb = cls._wait_for_lb_active(lb[const.ID])
        return lb

    @classmethod
    def _lb_kwargs(cls, port_id, name):
        return {const.NAME: data_utils.rand_name(
                    'lb_member_lb-vip_port-{}'.format(name)),
                const.PROVIDER: CONF.load_balancer.provider,
                const.VIP_PORT_ID: port_id}

    @classmethod
    def _wait_for_lb_active(cls, lb_id):
        return waiters.wait_for_status(
            cls.mem_lb_client.show_loadbalancer, lb_id,
            const.PROVISIONING_STATUS, const.ACTIVE,
            CONF.load_balancer.lb_build_interval,
            CONF.load_balancer.lb_build_timeout)

    def _delete_lb(self, lb_id):
        self.mem_lb_client.delete_loadbalancer(lb_id)
        waiters.wait_for_deleted_status_or_not_found(
            self.mem_lb_client.show_loadbalancer, lb_id,
            const.PROVISIONING_STATUS,
            CONF.load_balancer.lb_build_interval,
            CONF.load_balancer.lb_build_timeout)

    def _show_port(self, port_id):
        return self.admin_ports_client.show_port(port_id)['port']

    def _assert_port_claimed(self, port_id, lb_id):
        """The port is in use by the load balancer and bound to a host."""
        port = self._show_port(port_id)
        message = 'VIP port {} is not claimed by load balancer {}.'.format(
            port_id, lb_id)
        self.assertEqual(F5_VIP_PORT_DEVICE_OWNER, port[DEVICE_OWNER],
                         message)
        self.assertEqual(lb_id, port[DEVICE_ID], message)
        self.assertTrue(port[BINDING_HOST_ID],
                        'VIP port {} of load balancer {} is not bound to a '
                        'host.'.format(port_id, lb_id))
        return port

    def _assert_port_released(self, port_id, original):
        """The port still exists, nothing set by the claim is left.

        :param original: The port before it was claimed.
        """
        try:
            port = self._show_port(port_id)
        except exceptions.NotFound:
            self.fail('VIP port {} was deleted, it belongs to the project and '
                      'should have been handed back.'.format(port_id))
        message = 'VIP port {} was not handed back.'.format(port_id)
        self.assertEqual('', port[DEVICE_OWNER], message)
        self.assertEqual('', port[DEVICE_ID], message)
        self.assertEqual('', port[BINDING_HOST_ID], message)
        self.assertEqual([], port[ALLOWED_ADDRESS_PAIRS], message)
        self.assertEqual(original[const.NAME], port[const.NAME])
        self.assertEqual(original[FIXED_IPS], port[FIXED_IPS])
        return port

    def _assert_lb_create_refused(self, exc_classes, port_id, name, **kwargs):
        """Create a load balancer that must be refused.

        :param exc_classes: The expected exception class(es).
        :returns: The exception.
        """
        lb_kwargs = self._lb_kwargs(port_id, name)
        lb_kwargs.update(kwargs)
        try:
            lb = self.mem_lb_client.create_loadbalancer(**lb_kwargs)
        except exc_classes as e:
            self._assert_no_lb_named(lb_kwargs[const.NAME])
            return e
        self.addCleanup(self.mem_lb_client.cleanup_loadbalancer, lb[const.ID])
        self.fail('Load balancer {} was created on VIP port {}, it should '
                  'have been refused.'.format(lb[const.ID], port_id))

    def _assert_no_lb_named(self, name):
        """A refused create left no load balancer behind."""
        lbs = self.mem_lb_client.list_loadbalancers(
            query_params='{}={}'.format(const.NAME, name))
        self.assertEqual([], [lb[const.ID] for lb in lbs
                              if lb[const.PROVISIONING_STATUS] !=
                              const.DELETED])

    def _lb_hosts(self, lb_id):
        """Hosts that provision the load balancer.

        The F5 worker that creates a load balancer records itself in the
        compute_flavor of the amphora entry of the load balancer.
        """
        try:
            amphorae = self.admin_amphora_client.list_amphorae(
                query_params='{}={}'.format(const.LOADBALANCER_ID, lb_id))
        except exceptions.Forbidden:
            raise self.skipException('The admin may not list amphorae.')
        self.assertNotEqual([], amphorae,
                            'No amphora entry for load balancer {}.'.format(
                                lb_id))
        return {amphora[const.COMPUTE_FLAVOR] for amphora in amphorae}

    def _availability_zones(self):
        """Hosts of every availability zone, and the zones to test.

        :returns: ({zone name: set of hosts}, [enabled zones of the provider
            that list hosts])
        """
        hosts = {}
        usable = []
        try:
            for zone in self.admin_az_client.list_availability_zones():
                profile = (
                    self.admin_az_profile_client
                    .show_availability_zone_profile(
                        zone[const.AVAILABILITY_ZONE_PROFILE_ID]))
                data = json.loads(
                    profile[const.AVAILABILITY_ZONE_DATA] or '{}')
                hosts[zone[const.NAME]] = set(data.get(HOSTS) or [])
                if (zone[const.ENABLED] and hosts[zone[const.NAME]] and
                        profile[const.PROVIDER_NAME] ==
                        CONF.load_balancer.provider):
                    usable.append(zone[const.NAME])
        except exceptions.Forbidden:
            raise self.skipException(
                'The admin may not show availability zone profiles.')
        return hosts, sorted(usable)

    @decorators.idempotent_id('a90465f1-93b7-4d48-9971-bd38da55d405')
    def test_vip_port_claimed_by_load_balancer(self):
        """The load balancer claims the VIP port passed as vip_port_id.

        * The load balancer uses the port and its IP address.
        * device_owner and device_id show that the load balancer uses the
          port: Neutron keeps the project from deleting it, Octavia refuses
          it for further load balancers.
        * The port is bound to a host.
        * Name, fixed IPs and project of the port do not change.
        """
        port = self.shared_port
        lb = self.mem_lb_client.show_loadbalancer(self.shared_lb[const.ID])

        self.assertEqual(port[const.ID], lb[const.VIP_PORT_ID])
        self.assertEqual(port[NETWORK_ID], lb[const.VIP_NETWORK_ID])
        self.assertEqual(port[FIXED_IPS][0][const.SUBNET_ID],
                         lb[const.VIP_SUBNET_ID])
        self.assertEqual(port[FIXED_IPS][0][IP_ADDRESS],
                         lb[const.VIP_ADDRESS])

        # As created by the project
        self.assertEqual('', port[DEVICE_OWNER])
        self.assertEqual('', port[DEVICE_ID])

        claimed = self._assert_port_claimed(port[const.ID], lb[const.ID])
        self.assertEqual(port[const.NAME], claimed[const.NAME])
        self.assertEqual(port[FIXED_IPS], claimed[FIXED_IPS])
        self.assertEqual(port[const.PROJECT_ID], claimed[const.PROJECT_ID])

    @decorators.idempotent_id('201ea380-bbfe-49b8-a0a1-29b41c3d38e4')
    def test_vip_port_bound_to_load_balancer_host(self):
        """The load balancer is created on the host its VIP port is bound to.

        Without the binding, the create request went to any worker, maybe one
        in another availability zone than the port's network.
        """
        port = self._show_port(self.shared_port[const.ID])
        hosts = self._lb_hosts(self.shared_lb[const.ID])

        self.assertEqual({port[BINDING_HOST_ID]}, hosts,
                         'Load balancer {} is created on {}, its VIP port is '
                         'bound to {!r}.'.format(self.shared_lb[const.ID],
                                                 ', '.join(sorted(hosts)),
                                                 port[BINDING_HOST_ID]))

    @decorators.idempotent_id('3e2121fe-2de3-4654-85bd-be11fa0f7465')
    def test_vip_port_in_use_refused(self):
        """A second load balancer on a claimed VIP port is refused.

        * Create a load balancer on the VIP port of another load balancer.
        * Validate it is refused (400) and not created.
        * Validate the port and the first load balancer are unchanged.
        """
        exc = self._assert_lb_create_refused(
            exceptions.BadRequest, self.shared_port[const.ID], 'in_use')
        self.assertIn(self.shared_lb[const.ID], str(exc))

        self._assert_port_claimed(self.shared_port[const.ID],
                                  self.shared_lb[const.ID])
        lb = self.mem_lb_client.show_loadbalancer(self.shared_lb[const.ID])
        self.assertEqual(const.ACTIVE, lb[const.PROVISIONING_STATUS])

    @decorators.idempotent_id('e38d7862-9e09-428f-8ded-5d2b5fc73ea5')
    def test_vip_port_created_by_octavia(self):
        """A VIP port created by Octavia: refused, deleted with its owner.

        * Create a load balancer without vip_port_id.
        * Validate its VIP port is refused for a second load balancer.
        * Delete the load balancer.
        * Validate its VIP port is deleted as well.
        """
        lb = self.mem_lb_client.create_loadbalancer(
            name=data_utils.rand_name('lb_member_lb-vip_port-octavia'),
            provider=CONF.load_balancer.provider,
            vip_network_id=self.lb_member_vip_net[const.ID])
        self.addCleanup(self.mem_lb_client.cleanup_loadbalancer, lb[const.ID])
        lb = self._wait_for_lb_active(lb[const.ID])
        port_id = lb[const.VIP_PORT_ID]
        self._assert_port_claimed(port_id, lb[const.ID])

        exc = self._assert_lb_create_refused(exceptions.BadRequest, port_id,
                                             'octavia_port')
        self.assertIn(lb[const.ID], str(exc))

        self._delete_lb(lb[const.ID])
        self.assertRaises(exceptions.NotFound, self._show_port, port_id)

    @decorators.idempotent_id('0811d55d-d491-400b-a5f8-923410c3c06d')
    def test_vip_port_released_on_load_balancer_delete(self):
        """Deleting the load balancer hands the VIP port back.

        * Create a load balancer on a VIP port of the project.
        * Delete the load balancer.
        * Validate the port still exists, without device_owner, device_id,
          host binding and allowed address pairs.
        * Validate the project can delete the port.
        """
        port = self._create_vip_port(self.addCleanup)
        lb = self._create_lb_on_port(self.addCleanup, port[const.ID],
                                     'release')
        self._assert_port_claimed(port[const.ID], lb[const.ID])

        self._delete_lb(lb[const.ID])

        self._assert_port_released(port[const.ID], port)
        self.lb_mem_ports_client.delete_port(port[const.ID])
        self.assertRaises(exceptions.NotFound,
                          self.lb_mem_ports_client.show_port, port[const.ID])

    @decorators.idempotent_id('ce593166-18f0-4215-b5c3-7fb90ce0a56c')
    def test_vip_port_reused_after_load_balancer_delete(self):
        """A released VIP port can be used for a new load balancer.

        * Create a load balancer on a VIP port, delete it.
        * Create a new load balancer on the same port.
        * Validate the new load balancer is ACTIVE and claims the port.
        """
        port = self._create_vip_port(self.addCleanup)
        lb = self._create_lb_on_port(self.addCleanup, port[const.ID],
                                     'first')
        self._delete_lb(lb[const.ID])

        lb = self._create_lb_on_port(self.addCleanup, port[const.ID],
                                     'reuse')

        self.assertEqual(port[const.ID], lb[const.VIP_PORT_ID])
        self.assertEqual(port[FIXED_IPS][0][IP_ADDRESS],
                         lb[const.VIP_ADDRESS])
        self._assert_port_claimed(port[const.ID], lb[const.ID])

    @decorators.idempotent_id('73424f91-743f-4b7a-aa55-ba4e245681bd')
    def test_vip_port_delete_forbidden(self):
        """The project cannot delete the VIP port of its load balancer.

        Deleting it would break the load balancer. Neutron refuses it because
        of the device_owner the port got (policy: ports with device_owner
        network:* are deleted by cloud admins only).
        """
        port = self._create_vip_port(self.addCleanup)
        lb = self._create_lb_on_port(self.addCleanup, port[const.ID],
                                     'protected')
        # Without the claim nothing protects the port, and deleting it would
        # break the load balancer: fail here instead
        self._assert_port_claimed(port[const.ID], lb[const.ID])

        try:
            self.lb_mem_ports_client.delete_port(port[const.ID])
        except exceptions.Forbidden:
            pass
        else:
            self.fail('The project deleted VIP port {} of load balancer '
                      '{}.'.format(port[const.ID], lb[const.ID]))

        self._assert_port_claimed(port[const.ID], lb[const.ID])

    @decorators.idempotent_id('5a91f1f8-c4dd-4a6b-92a8-4b90cebf0552')
    def test_vip_port_released_when_create_fails(self):
        """A create that fails after the claim hands the VIP port back.

        * Create a load balancer on a VIP port with a listener that refers
          to an undefined pool. Octavia refuses it after the provider has
          claimed the port.
        * Validate the port was claimed (revision changed), handed back and
          not deleted.
        """
        port = self._create_vip_port(self.addCleanup)
        before = self._show_port(port[const.ID])
        listener = {const.NAME: 'listener', const.PROTOCOL: const.HTTP,
                    const.PROTOCOL_PORT: 80,
                    DEFAULT_POOL: {const.NAME: 'undefined_pool'}}

        exc = self._assert_lb_create_refused(
            exceptions.BadRequest, port[const.ID], 'create_fails',
            listeners=[listener])
        self.assertIn('undefined_pool', str(exc))

        after = self._assert_port_released(port[const.ID], before)
        # One update to claim the port, one to release it (at least)
        self.assertGreaterEqual(
            after[REVISION_NUMBER], before[REVISION_NUMBER] + 2,
            'VIP port {} was not claimed before the create failed.'.format(
                port[const.ID]))

    @decorators.idempotent_id('a9669e03-aed7-46fd-83b4-05aa951ee0ec')
    def test_vip_port_of_older_load_balancer_refused(self):
        """The VIP port of a load balancer from before claiming is refused.

        Such ports have neither device_owner nor device_id, so only the
        Octavia DB knows that a load balancer uses them.

        * Create a load balancer on a VIP port.
        * Clear device_owner and device_id of the port, as an admin.
        * Validate a second load balancer on the port is refused (409) and
          the port is not claimed by it.
        """
        port = self._create_vip_port(self.addCleanup)
        lb = self._create_lb_on_port(self.addCleanup, port[const.ID],
                                     'older')
        self.admin_ports_client.update_port(
            port[const.ID], **{DEVICE_OWNER: '', DEVICE_ID: ''})

        exc = self._assert_lb_create_refused(
            exceptions.Conflict, port[const.ID], 'older_second')
        self.assertIn(lb[const.ID], str(exc))

        port = self._show_port(port[const.ID])
        self.assertEqual('', port[DEVICE_OWNER])
        self.assertEqual('', port[DEVICE_ID])
        lb = self.mem_lb_client.show_loadbalancer(lb[const.ID])
        self.assertEqual(const.ACTIVE, lb[const.PROVISIONING_STATUS])

    @decorators.idempotent_id('a85857f2-f957-4b62-89d0-4c8b34bd56e1')
    def test_vip_port_concurrent_creates(self):
        """Only one of concurrent creates on the same VIP port succeeds.

        * Send three creates on the same VIP port at the same time.
        * Validate one load balancer is created and claims the port.
        * Validate the others are refused (400 or 409) and not created.
        """
        port = self._create_vip_port(self.addCleanup)
        names = [data_utils.rand_name('lb_member_lb-vip_port-concurrent')
                 for _ in range(3)]
        # A client per thread
        lb_v2 = self.os_roles_lb_member.load_balancer_v2
        clients = [lb_v2.LoadbalancerClient() for _ in names]
        start = threading.Barrier(len(names))

        def create(client, name):
            start.wait(timeout=CONF.load_balancer.check_timeout)
            try:
                return client.create_loadbalancer(
                    name=name, provider=CONF.load_balancer.provider,
                    vip_port_id=port[const.ID])
            except Exception as e:
                return e

        with futures.ThreadPoolExecutor(max_workers=len(names)) as executor:
            results = list(executor.map(create, clients, names))

        created = [r for r in results if not isinstance(r, Exception)]
        for lb in created:
            self.addCleanup(self.mem_lb_client.cleanup_loadbalancer,
                            lb[const.ID])
        self.assertEqual(
            1, len(created),
            'Concurrent creates on VIP port {}: {}'.format(
                port[const.ID],
                ', '.join(repr(r) if isinstance(r, Exception) else
                          'created ' + r[const.ID] for r in results)))
        for name, result in zip(names, results):
            if isinstance(result, Exception):
                self.assertIsInstance(
                    result, (exceptions.BadRequest, exceptions.Conflict))
                self._assert_no_lb_named(name)

        lb = self._wait_for_lb_active(created[0][const.ID])
        self._assert_port_claimed(port[const.ID], lb[const.ID])

    @decorators.idempotent_id('6966a9d4-174b-4244-9867-a26aef31426d')
    def test_vip_port_bound_in_availability_zone(self):
        """The VIP port is bound to a host of the load balancer's zone.

        * Create a load balancer on a VIP port in every enabled availability
          zone of the provider, and one without zone.
        * Validate each port is bound to a host of the zone; without zone, to
          a host that is in no zone.
        * Validate each load balancer is created on that host.
        """
        hosts, zones = self._availability_zones()
        if not zones:
            raise self.skipException(
                'No availability zone of provider {} lists hosts.'.format(
                    CONF.load_balancer.provider))

        lbs = []
        for zone in zones + [None]:
            port = self._create_vip_port(self.addCleanup)
            kwargs = {const.AVAILABILITY_ZONE: zone} if zone else {}
            lb = self._create_lb_on_port(
                self.addCleanup, port[const.ID], zone or 'no_zone',
                wait=False, **kwargs)
            lbs.append((port[const.ID], lb))

        hosts_in_zones = set().union(*hosts.values())
        for port_id, lb in lbs:
            # The zone the load balancer got, in case there is a default
            zone = lb.get(const.AVAILABILITY_ZONE)
            lb_id = lb[const.ID]
            host = self._show_port(port_id)[BINDING_HOST_ID]
            if zone:
                self.assertIn(host, hosts.get(zone, set()),
                              'VIP port {} of load balancer {} is bound to '
                              'a host not in zone {}.'.format(port_id, lb_id,
                                                              zone))
            else:
                self.assertNotIn(host, hosts_in_zones,
                                 'VIP port {} of load balancer {} without '
                                 'zone is bound to a host of a zone.'.format(
                                     port_id, lb_id))
            self._wait_for_lb_active(lb_id)
            self.assertEqual({host}, self._lb_hosts(lb_id),
                             'Load balancer {} is not created on {!r}, the '
                             'host its VIP port is bound to.'.format(lb_id,
                                                                     host))
