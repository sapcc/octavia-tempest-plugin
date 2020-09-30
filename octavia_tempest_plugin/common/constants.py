# Copyright 2018 Rackspace US Inc.  All rights reserved.
#
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

# API field names
ACTIVE_CONNECTIONS = 'active_connections'
ALLOWED_CIDRS = 'allowed_cidrs'
AVAILABILITY_ZONE = 'availability_zone'
AVAILABILITY_ZONE_DATA = 'availability_zone_data'
AVAILABILITY_ZONE_PROFILE_ID = 'availability_zone_profile_id'
ADMIN_STATE_UP = 'admin_state_up'
BYTES_IN = 'bytes_in'
BYTES_OUT = 'bytes_out'
CA_TLS_CONTAINER_REF = 'ca_tls_container_ref'
CLIENT_AUTHENTICATION = 'client_authentication'
CLIENT_AUTH_NONE = 'NONE'
CLIENT_AUTH_OPTIONAL = 'OPTIONAL'
CLIENT_AUTH_MANDATORY = 'MANDATORY'
CLIENT_CA_TLS_CONTAINER_REF = 'client_ca_tls_container_ref'
CLIENT_CRL_CONTAINER_REF = 'client_crl_container_ref'
CREATED_AT = 'created_at'
CRL_CONTAINER_REF = 'crl_container_ref'
DESCRIPTION = 'description'
FLAVOR_DATA = 'flavor_data'
FLAVOR_ID = 'flavor_id'
FLAVOR_PROFILE_ID = 'flavor_profile_id'
ID = 'id'
LISTENERS = 'listeners'
LOADBALANCER = 'loadbalancer'
NAME = 'name'
OPERATING_STATUS = 'operating_status'
POOLS = 'pools'
PROJECT_ID = 'project_id'
PROVIDER = 'provider'
PROVIDER_NAME = 'provider_name'
PROVISIONING_STATUS = 'provisioning_status'
REQUEST_ERRORS = 'request_errors'
TLS_CONTAINER_REF = 'tls_container_ref'
TOTAL_CONNECTIONS = 'total_connections'
UPDATED_AT = 'updated_at'
VIP_ADDRESS = 'vip_address'
VIP_NETWORK_ID = 'vip_network_id'
VIP_PORT_ID = 'vip_port_id'
VIP_SUBNET_ID = 'vip_subnet_id'
VIP_QOS_POLICY_ID = 'vip_qos_policy_id'
PROTOCOL = 'protocol'
PROTOCOL_PORT = 'protocol_port'
LOADBALANCER_ID = 'loadbalancer_id'
CONNECTION_LIMIT = 'connection_limit'
INSERT_HEADERS = 'insert_headers'
X_FORWARDED_FOR = 'X-Forwarded-For'
X_FORWARDED_PORT = 'X-Forwarded-Port'
X_FORWARDED_PROTO = 'X-Forwarded-Proto'
TAGS = 'tags'
TIMEOUT_CLIENT_DATA = 'timeout_client_data'
TIMEOUT_MEMBER_CONNECT = 'timeout_member_connect'
TIMEOUT_MEMBER_DATA = 'timeout_member_data'
TIMEOUT_TCP_INSPECT = 'timeout_tcp_inspect'
TLS_ENABLED = 'tls_enabled'
DEFAULT_TLS_CONTAINER_REF = 'default_tls_container_ref'
SNI_CONTAINER_REFS = 'sni_container_refs'
DEFAULT_POOL_ID = 'default_pool_id'
L7_POLICIES = 'l7_policies'
ALPN_PROTOCOLS = 'alpn_protocols'

LB_ALGORITHM = 'lb_algorithm'
LB_ALGORITHM_ROUND_ROBIN = 'ROUND_ROBIN'
LB_ALGORITHM_LEAST_CONNECTIONS = 'LEAST_CONNECTIONS'
LB_ALGORITHM_SOURCE_IP = 'SOURCE_IP'
LB_ALGORITHM_SOURCE_IP_PORT = 'SOURCE_IP_PORT'
SUPPORTED_LB_ALGORITHMS_AMPHORA = [
    LB_ALGORITHM_ROUND_ROBIN,
    LB_ALGORITHM_LEAST_CONNECTIONS,
    LB_ALGORITHM_SOURCE_IP]
SUPPORTED_LB_ALGORITHMS = {
    'default': SUPPORTED_LB_ALGORITHMS_AMPHORA,
    'octavia': SUPPORTED_LB_ALGORITHMS_AMPHORA,
    'amphorav2': SUPPORTED_LB_ALGORITHMS_AMPHORA,
    'amphora': SUPPORTED_LB_ALGORITHMS_AMPHORA,
    'ovn': [LB_ALGORITHM_SOURCE_IP_PORT]}
SESSION_PERSISTENCE = 'session_persistence'
LISTENER_ID = 'listener_id'
LOADBALANCERS = 'loadbalancers'

POOL_ID = 'pool_id'
ADDRESS = 'address'
WEIGHT = 'weight'
BACKUP = 'backup'
SUBNET_ID = 'subnet_id'
MONITOR_ADDRESS = 'monitor_address'
MONITOR_PORT = 'monitor_port'

DELAY = 'delay'
TIMEOUT = 'timeout'
MAX_RETRIES = 'max_retries'
MAX_RETRIES_DOWN = 'max_retries_down'
HTTP_METHOD = 'http_method'
URL_PATH = 'url_path'
EXPECTED_CODES = 'expected_codes'

ENABLED = 'enabled'

# Other constants
ACTIVE = 'ACTIVE'
PENDING_UPDATE = 'PENDING_UPDATE'
ADMIN_STATE_UP_TRUE = 'true'
ASC = 'asc'
DELETED = 'DELETED'
DESC = 'desc'
DRAINING = "DRAINING"
FIELDS = 'fields'
OFFLINE = 'OFFLINE'
ONLINE = 'ONLINE'
NO_MONITOR = 'NO_MONITOR'
ERROR = 'ERROR'
SORT = 'sort'
SINGLE = 'SINGLE'
ACTIVE_STANDBY = 'ACTIVE_STANDBY'
SUPPORTED_LB_TOPOLOGIES = (SINGLE, ACTIVE_STANDBY)

# Protocols
HTTP = 'HTTP'
HTTPS = 'HTTPS'
PROXY = 'PROXY'
TCP = 'TCP'
TERMINATED_HTTPS = 'TERMINATED_HTTPS'
UDP = 'UDP'

# HTTP Methods
GET = 'GET'
POST = 'POST'
PUT = 'PUT'
DELETE = 'DELETE'
HEAD = 'HEAD'
OPTIONS = 'OPTIONS'
PATCH = 'PATCH'
CONNECT = 'CONNECT'
TRACE = 'TRACE'

# HM Types
HEALTH_MONITOR_PING = 'PING'
HEALTH_MONITOR_TCP = 'TCP'
HEALTH_MONITOR_HTTP = 'HTTP'
HEALTH_MONITOR_HTTPS = 'HTTPS'
HEALTH_MONITOR_TLS_HELLO = 'TLS-HELLO'
HEALTH_MONITOR_UDP_CONNECT = 'UDP-CONNECT'

# Session Persistence
TYPE = 'type'
COOKIE_NAME = 'cookie_name'
SESSION_PERSISTENCE_SOURCE_IP = 'SOURCE_IP'
SESSION_PERSISTENCE_HTTP_COOKIE = 'HTTP_COOKIE'
SESSION_PERSISTENCE_APP_COOKIE = 'APP_COOKIE'

# L7Policy options
POSITION = 'position'
REDIRECT_URL = 'redirect_url'
REDIRECT_POOL_ID = 'redirect_pool_id'

ACTION = 'action'
REDIRECT_TO_POOL = 'REDIRECT_TO_POOL'
REDIRECT_TO_URL = 'REDIRECT_TO_URL'
REJECT = 'REJECT'

# L7Rule options
L7POLICY_ID = 'l7policy_id'
VALUE = 'value'
COMPARE_TYPE = 'compare_type'
KEY = 'key'
INVERT = 'invert'
# Compare types
EQUAL_TO = 'EQUAL_TO'
STARTS_WITH = 'STARTS_WITH'
ENDS_WITH = 'ENDS_WITH'
CONTAINS = 'CONTAINS'
REGEX = 'REGEX'
# Types
COOKIE = 'COOKIE'
FILE_TYPE = 'FILE_TYPE'
HEADER = 'HEADER'
HOST_NAME = 'HOST_NAME'
PATH = 'PATH'

# RBAC options
ADVANCED = 'advanced'
KEYSTONE_DEFAULT_ROLES = 'keystone_default_roles'
OWNERADMIN = 'owner_or_admin'
NONE = 'none'

# Amphora fields
COMPUTE_ID = 'compute_id'
LB_NETWORK_IP = 'lb_network_ip'
VRRP_IP = 'vrrp_ip'
HA_IP = 'ha_ip'
VRRP_PORT_ID = 'vrrp_port_id'
HA_PORT_ID = 'ha_port_id'
CERT_EXPIRATION = 'cert_expiration'
CERT_BUSY = 'cert_busy'
ROLE = 'role'
STATUS = 'status'
VRRP_INTERFACE = 'vrrp_interface'
VRRP_ID = 'vrrp_id'
VRRP_PRIORITY = 'vrrp_priority'
CACHED_ZONE = 'cached_zone'
IMAGE_ID = 'image_id'

# Amphora roles
ROLE_STANDALONE = 'STANDALONE'
ROLE_MASTER = 'MASTER'
ROLE_BACKUP = 'BACKUP'
AMPHORA_ROLES = (ROLE_STANDALONE, ROLE_MASTER, ROLE_BACKUP)

# Amphora statuses
STATUS_BOOTING = 'BOOTING'
STATUS_ALLOCATED = 'ALLOCATED'
STATUS_READY = 'READY'
STATUS_PENDING_CREATE = 'PENDING_CREATE'
STATUS_PENDING_DELETE = 'PENDING_DELETE'
STATUS_DELETED = 'DELETED'
STATUS_ERROR = 'ERROR'
AMPHORA_STATUSES = (
    STATUS_BOOTING, STATUS_ALLOCATED, STATUS_READY, STATUS_PENDING_CREATE,
    STATUS_PENDING_DELETE, STATUS_DELETED, STATUS_ERROR
)

# Amphora providers list
AMPHORA_PROVIDERS = ['amphora', 'amphorav2', 'octavia']

# Flavor capabilities
LOADBALANCER_TOPOLOGY = 'loadbalancer_topology'

# Availability zone capabilities
COMPUTE_ZONE = 'compute_zone'
MANAGEMENT_NETWORK = 'management_network'

# API valid fields
SHOW_LOAD_BALANCER_RESPONSE_FIELDS = (
    ADMIN_STATE_UP, CREATED_AT, DESCRIPTION, FLAVOR_ID, ID, LISTENERS, NAME,
    OPERATING_STATUS, POOLS, PROJECT_ID, PROVIDER, PROVISIONING_STATUS,
    UPDATED_AT, VIP_ADDRESS, VIP_NETWORK_ID, VIP_PORT_ID, VIP_SUBNET_ID,
    VIP_QOS_POLICY_ID)

SHOW_LISTENER_RESPONSE_FIELDS = [
    ID, NAME, DESCRIPTION, PROVISIONING_STATUS, OPERATING_STATUS,
    ADMIN_STATE_UP, PROTOCOL, PROTOCOL_PORT, CONNECTION_LIMIT,
    DEFAULT_TLS_CONTAINER_REF, SNI_CONTAINER_REFS, PROJECT_ID,
    DEFAULT_POOL_ID, L7_POLICIES, INSERT_HEADERS, CREATED_AT, UPDATED_AT
]

SHOW_POOL_RESPONSE_FIELDS = (
    ID, NAME, DESCRIPTION, PROVISIONING_STATUS, OPERATING_STATUS,
    ADMIN_STATE_UP, PROTOCOL, LB_ALGORITHM, SESSION_PERSISTENCE,
    CREATED_AT, UPDATED_AT
)

SHOW_MEMBER_RESPONSE_FIELDS = [
    ID, NAME, PROVISIONING_STATUS, OPERATING_STATUS, ADMIN_STATE_UP,
    ADDRESS, PROTOCOL_PORT, WEIGHT, MONITOR_PORT, MONITOR_ADDRESS
]

SHOW_HEALTHMONITOR_RESPONSE_FIELDS = (
    ID, NAME, PROVISIONING_STATUS, OPERATING_STATUS, ADMIN_STATE_UP,
    TYPE, DELAY, TIMEOUT, MAX_RETRIES, MAX_RETRIES_DOWN, HTTP_METHOD,
    URL_PATH, EXPECTED_CODES, CREATED_AT, UPDATED_AT
)

SHOW_L7POLICY_RESPONSE_FIELDS = (
    ID, NAME, DESCRIPTION, PROVISIONING_STATUS, OPERATING_STATUS,
    ADMIN_STATE_UP, LISTENER_ID, POSITION, ACTION, REDIRECT_URL,
    REDIRECT_POOL_ID, CREATED_AT, UPDATED_AT
)

SHOW_L7RULE_RESPONSE_FIELDS = (
    ID, ADMIN_STATE_UP, CREATED_AT, UPDATED_AT, TYPE, VALUE, COMPARE_TYPE,
    KEY, INVERT
)

SHOW_AMPHORA_RESPONSE_FIELDS = [
    ID, LOADBALANCER_ID, COMPUTE_ID, LB_NETWORK_IP, VRRP_IP, HA_IP,
    VRRP_PORT_ID, HA_PORT_ID, CERT_EXPIRATION, CERT_BUSY, ROLE, STATUS,
    VRRP_INTERFACE, VRRP_ID, VRRP_PRIORITY, CACHED_ZONE
]

SHOW_FLAVOR_PROFILE_FIELDS = [ID, NAME, PROVIDER_NAME, FLAVOR_DATA]

SHOW_FLAVOR_FIELDS = [ID, NAME, DESCRIPTION, ENABLED, FLAVOR_PROFILE_ID]

SHOW_AVAILABILITY_ZONE_PROFILE_FIELDS = [
    ID, NAME, PROVIDER_NAME, AVAILABILITY_ZONE_DATA]

SHOW_AVAILABILITY_ZONE_FIELDS = [
    NAME, DESCRIPTION, ENABLED, AVAILABILITY_ZONE_PROFILE_ID]

# Paths inside the test webservers
CERT_PEM = 'cert.pem'
KEY_PEM = 'key.pem'
CLIENT_CA_PEM = 'client_ca.pem'
DEV_SHM_PATH = '/home/ccloud/'
TEST_SERVER_BINARY = DEV_SHM_PATH + 'test_server.bin'
TEST_SERVER_CERT = DEV_SHM_PATH + CERT_PEM
TEST_SERVER_KEY = DEV_SHM_PATH + KEY_PEM
TEST_SERVER_CLIENT_CA = DEV_SHM_PATH + CLIENT_CA_PEM
