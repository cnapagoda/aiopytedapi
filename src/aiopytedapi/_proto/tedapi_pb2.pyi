from google.protobuf import timestamp_pb2 as _timestamp_pb2
from google.protobuf import wrappers_pb2 as _wrappers_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Domain(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    DOMAIN_BROADCAST: _ClassVar[Domain]
    DOMAIN_VEHICLE_SECURITY: _ClassVar[Domain]
    DOMAIN_INFOTAINMENT: _ClassVar[Domain]
    DOMAIN_AUTHD: _ClassVar[Domain]
    DOMAIN_ENERGY_DEVICE: _ClassVar[Domain]
    DOMAIN_ENERGY_DEVICE_AUTH: _ClassVar[Domain]

class Flags(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    FLAGS_NONE: _ClassVar[Flags]

class MessageFault_E(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    MESSAGEFAULT_ERROR_NONE: _ClassVar[MessageFault_E]
    MESSAGEFAULT_ERROR_BUSY: _ClassVar[MessageFault_E]
    MESSAGEFAULT_ERROR_TIMEOUT: _ClassVar[MessageFault_E]
    MESSAGEFAULT_ERROR_UNKNOWN_KEY_ID: _ClassVar[MessageFault_E]
    MESSAGEFAULT_ERROR_INACTIVE_KEY: _ClassVar[MessageFault_E]
    MESSAGEFAULT_ERROR_INVALID_SIGNATURE: _ClassVar[MessageFault_E]
    MESSAGEFAULT_ERROR_INVALID_TOKEN_OR_COUNTER: _ClassVar[MessageFault_E]
    MESSAGEFAULT_ERROR_INSUFFICIENT_PRIVILEGES: _ClassVar[MessageFault_E]
    MESSAGEFAULT_ERROR_INVALID_DOMAINS: _ClassVar[MessageFault_E]
    MESSAGEFAULT_ERROR_INVALID_COMMAND: _ClassVar[MessageFault_E]
    MESSAGEFAULT_ERROR_DECODING: _ClassVar[MessageFault_E]
    MESSAGEFAULT_ERROR_INTERNAL: _ClassVar[MessageFault_E]
    MESSAGEFAULT_ERROR_WRONG_PERSONALIZATION: _ClassVar[MessageFault_E]
    MESSAGEFAULT_ERROR_BAD_PARAMETER: _ClassVar[MessageFault_E]
    MESSAGEFAULT_ERROR_KEYCHAIN_IS_FULL: _ClassVar[MessageFault_E]
    MESSAGEFAULT_ERROR_INCORRECT_EPOCH: _ClassVar[MessageFault_E]
    MESSAGEFAULT_ERROR_IV_INCORRECT_LENGTH: _ClassVar[MessageFault_E]
    MESSAGEFAULT_ERROR_TIME_EXPIRED: _ClassVar[MessageFault_E]
    MESSAGEFAULT_ERROR_NOT_PROVISIONED_WITH_IDENTITY: _ClassVar[MessageFault_E]
    MESSAGEFAULT_ERROR_COULD_NOT_HASH_METADATA: _ClassVar[MessageFault_E]
    MESSAGEFAULT_ERROR_TIME_TO_LIVE_TOO_LONG: _ClassVar[MessageFault_E]
    MESSAGEFAULT_ERROR_REMOTE_ACCESS_DISABLED: _ClassVar[MessageFault_E]
    MESSAGEFAULT_ERROR_REMOTE_SERVICE_REQUEST_NOT_SUPPORTED: _ClassVar[MessageFault_E]

class SignatureType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    SIGNATURE_TYPE_AES_GCM: _ClassVar[SignatureType]
    SIGNATURE_TYPE_ECDSA: _ClassVar[SignatureType]
    SIGNATURE_TYPE_PRESENT_KEY: _ClassVar[SignatureType]
    SIGNATURE_TYPE_AES_GCM_TOKEN: _ClassVar[SignatureType]
    SIGNATURE_TYPE_ECDSA_PERSONALIZED: _ClassVar[SignatureType]
    SIGNATURE_TYPE_AES_GCM_PERSONALIZED: _ClassVar[SignatureType]
    SIGNATURE_TYPE_HMAC: _ClassVar[SignatureType]
    SIGNATURE_TYPE_RSA: _ClassVar[SignatureType]
    SIGNATURE_TYPE_HMAC_PERSONALIZED: _ClassVar[SignatureType]
    SIGNATURE_TYPE_AES_GCM_RESPONSE: _ClassVar[SignatureType]

class Tag(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    TAG_SIGNATURE_TYPE: _ClassVar[Tag]
    TAG_DOMAIN: _ClassVar[Tag]
    TAG_PERSONALIZATION: _ClassVar[Tag]
    TAG_EPOCH: _ClassVar[Tag]
    TAG_EXPIRES_AT: _ClassVar[Tag]
    TAG_COUNTER: _ClassVar[Tag]
    TAG_CHALLENGE: _ClassVar[Tag]
    TAG_FLAGS: _ClassVar[Tag]
    TAG_REQUEST_HASH: _ClassVar[Tag]
    TAG_FAULT: _ClassVar[Tag]
    TAG_END: _ClassVar[Tag]

class ExternalAuthType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    EXTERNAL_AUTH_TYPE_INVALID: _ClassVar[ExternalAuthType]
    EXTERNAL_AUTH_TYPE_PRESENCE: _ClassVar[ExternalAuthType]
    EXTERNAL_AUTH_TYPE_MTLS: _ClassVar[ExternalAuthType]
    EXTERNAL_AUTH_TYPE_HERMES_COMMAND: _ClassVar[ExternalAuthType]

class DeliveryChannel(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    DELIVERY_CHANNEL_INVALID: _ClassVar[DeliveryChannel]
    DELIVERY_CHANNEL_LOCAL_HTTPS: _ClassVar[DeliveryChannel]
    DELIVERY_CHANNEL_HERMES_COMMAND: _ClassVar[DeliveryChannel]
    DELIVERY_CHANNEL_BLE: _ClassVar[DeliveryChannel]

class LocalParticipant(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    LOCAL_PARTICIPANT_INVALID: _ClassVar[LocalParticipant]
    LOCAL_PARTICIPANT_INSTALLER: _ClassVar[LocalParticipant]
    LOCAL_PARTICIPANT_CUSTOMER: _ClassVar[LocalParticipant]

class TeslaService(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    TESLA_SERVICE_INVALID: _ClassVar[TeslaService]
    TESLA_SERVICE_COMMAND: _ClassVar[TeslaService]

class AuthorizedClientType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    AUTHORIZED_CLIENT_TYPE_INVALID: _ClassVar[AuthorizedClientType]
    AUTHORIZED_CLIENT_TYPE_CUSTOMER_MOBILE_APP: _ClassVar[AuthorizedClientType]
    AUTHORIZED_CLIENT_TYPE_VEHICLE: _ClassVar[AuthorizedClientType]

class WifiNetworkSecurityType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    WIFI_NETWORK_SECURITY_TYPE_INVALID: _ClassVar[WifiNetworkSecurityType]
    WIFI_NETWORK_SECURITY_TYPE_NONE: _ClassVar[WifiNetworkSecurityType]
    WIFI_NETWORK_SECURITY_TYPE_DYNAMIC_WEP: _ClassVar[WifiNetworkSecurityType]
    WIFI_NETWORK_SECURITY_TYPE_WPA2_PERSONAL: _ClassVar[WifiNetworkSecurityType]
    WIFI_NETWORK_SECURITY_TYPE_WPA2_ENTERPRISE: _ClassVar[WifiNetworkSecurityType]

class NetworkDeviceState(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    NETWORK_DEVICE_STATE_INVALID: _ClassVar[NetworkDeviceState]
    NETWORK_DEVICE_STATE_UNMANAGED: _ClassVar[NetworkDeviceState]
    NETWORK_DEVICE_STATE_UNAVAILABLE: _ClassVar[NetworkDeviceState]
    NETWORK_DEVICE_STATE_IDLE: _ClassVar[NetworkDeviceState]
    NETWORK_DEVICE_STATE_ASSOCIATION: _ClassVar[NetworkDeviceState]
    NETWORK_DEVICE_STATE_CONFIGURATION: _ClassVar[NetworkDeviceState]
    NETWORK_DEVICE_STATE_READY: _ClassVar[NetworkDeviceState]
    NETWORK_DEVICE_STATE_DISCONNECT: _ClassVar[NetworkDeviceState]
    NETWORK_DEVICE_STATE_FAILURE: _ClassVar[NetworkDeviceState]

class NetworkDeviceStateReason(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    NETWORK_DEVICE_STATE_REASON_INVALID: _ClassVar[NetworkDeviceStateReason]
    NETWORK_DEVICE_STATE_REASON_NONE: _ClassVar[NetworkDeviceStateReason]
    NETWORK_DEVICE_STATE_REASON_CONFIG_FAILED: _ClassVar[NetworkDeviceStateReason]
    NETWORK_DEVICE_STATE_REASON_DHCP_FAILED: _ClassVar[NetworkDeviceStateReason]
    NETWORK_DEVICE_STATE_REASON_IP_ADDRESS_DUPLICATE: _ClassVar[NetworkDeviceStateReason]
    NETWORK_DEVICE_STATE_REASON_IP_CONFIG_EXPIRED: _ClassVar[NetworkDeviceStateReason]
    NETWORK_DEVICE_STATE_REASON_IP_CONFIG_UNAVAILABLE: _ClassVar[NetworkDeviceStateReason]
    NETWORK_DEVICE_STATE_REASON_IP_METHOD_UNSUPPORTED: _ClassVar[NetworkDeviceStateReason]
    NETWORK_DEVICE_STATE_REASON_NEW_ACTIVATION: _ClassVar[NetworkDeviceStateReason]
    NETWORK_DEVICE_STATE_REASON_NO_SECRETS: _ClassVar[NetworkDeviceStateReason]
    NETWORK_DEVICE_STATE_REASON_PPP_FAILED: _ClassVar[NetworkDeviceStateReason]
    NETWORK_DEVICE_STATE_REASON_SSID_NOT_FOUND: _ClassVar[NetworkDeviceStateReason]
    NETWORK_DEVICE_STATE_REASON_SIM_PIN_INCORRECT: _ClassVar[NetworkDeviceStateReason]
    NETWORK_DEVICE_STATE_REASON_SUPPLICANT_FAILED: _ClassVar[NetworkDeviceStateReason]
    NETWORK_DEVICE_STATE_REASON_REMOVED: _ClassVar[NetworkDeviceStateReason]
    NETWORK_DEVICE_STATE_REASON_MODEM_FAILED: _ClassVar[NetworkDeviceStateReason]

class AuthorizedKeyType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    AUTHORIZED_KEY_TYPE_INVALID: _ClassVar[AuthorizedKeyType]
    AUTHORIZED_KEY_TYPE_RSA: _ClassVar[AuthorizedKeyType]
    AUTHORIZED_KEY_TYPE_ECC: _ClassVar[AuthorizedKeyType]

class AuthorizationRole(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    AUTHORIZATION_ROLE_INVALID: _ClassVar[AuthorizationRole]
    AUTHORIZATION_ROLE_CUSTOMER: _ClassVar[AuthorizationRole]
    AUTHORIZATION_ROLE_VEHICLE: _ClassVar[AuthorizationRole]

class AuthorizedState(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    AUTHORIZED_STATE_INVALID: _ClassVar[AuthorizedState]
    AUTHORIZED_STATE_PENDING_VERIFICATION: _ClassVar[AuthorizedState]
    AUTHORIZED_STATE_PENDING_VERIFICATION_TIMEOUT: _ClassVar[AuthorizedState]
    AUTHORIZED_STATE_VERIFIED: _ClassVar[AuthorizedState]
    AUTHORIZED_STATE_REMOVED: _ClassVar[AuthorizedState]

class AuthorizedVerificationType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    AUTHORIZED_VERIFICATION_TYPE_INVALID: _ClassVar[AuthorizedVerificationType]
    AUTHORIZED_VERIFICATION_TYPE_PRESENCE_PROOF: _ClassVar[AuthorizedVerificationType]
    AUTHORIZED_VERIFICATION_TYPE_BLE: _ClassVar[AuthorizedVerificationType]
    AUTHORIZED_VERIFICATION_TYPE_SIGNED: _ClassVar[AuthorizedVerificationType]
    AUTHORIZED_VERIFICATION_TYPE_HERMES_COMMAND: _ClassVar[AuthorizedVerificationType]

class FileStoreAPIDomain(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    FILE_STORE_API_DOMAIN_INVALID: _ClassVar[FileStoreAPIDomain]
    FILE_STORE_API_DOMAIN_CONFIG_JSON: _ClassVar[FileStoreAPIDomain]
    FILE_STORE_API_DOMAIN_GRID_CODE_REGIONS_CSV: _ClassVar[FileStoreAPIDomain]
    FILE_STORE_API_DOMAIN_CERTIFIED_INSTALLERS_CSV: _ClassVar[FileStoreAPIDomain]
    FILE_STORE_API_DOMAIN_SUPERCHARGER_FILES: _ClassVar[FileStoreAPIDomain]
    FILE_STORE_API_DOMAIN_OPTICASTER_FILES: _ClassVar[FileStoreAPIDomain]
    FILE_STORE_API_DOMAIN_WALLBOX_CONFIG: _ClassVar[FileStoreAPIDomain]
    FILE_STORE_API_DOMAIN_OCPP_CSMS_ROOT_CA: _ClassVar[FileStoreAPIDomain]
DOMAIN_BROADCAST: Domain
DOMAIN_VEHICLE_SECURITY: Domain
DOMAIN_INFOTAINMENT: Domain
DOMAIN_AUTHD: Domain
DOMAIN_ENERGY_DEVICE: Domain
DOMAIN_ENERGY_DEVICE_AUTH: Domain
FLAGS_NONE: Flags
MESSAGEFAULT_ERROR_NONE: MessageFault_E
MESSAGEFAULT_ERROR_BUSY: MessageFault_E
MESSAGEFAULT_ERROR_TIMEOUT: MessageFault_E
MESSAGEFAULT_ERROR_UNKNOWN_KEY_ID: MessageFault_E
MESSAGEFAULT_ERROR_INACTIVE_KEY: MessageFault_E
MESSAGEFAULT_ERROR_INVALID_SIGNATURE: MessageFault_E
MESSAGEFAULT_ERROR_INVALID_TOKEN_OR_COUNTER: MessageFault_E
MESSAGEFAULT_ERROR_INSUFFICIENT_PRIVILEGES: MessageFault_E
MESSAGEFAULT_ERROR_INVALID_DOMAINS: MessageFault_E
MESSAGEFAULT_ERROR_INVALID_COMMAND: MessageFault_E
MESSAGEFAULT_ERROR_DECODING: MessageFault_E
MESSAGEFAULT_ERROR_INTERNAL: MessageFault_E
MESSAGEFAULT_ERROR_WRONG_PERSONALIZATION: MessageFault_E
MESSAGEFAULT_ERROR_BAD_PARAMETER: MessageFault_E
MESSAGEFAULT_ERROR_KEYCHAIN_IS_FULL: MessageFault_E
MESSAGEFAULT_ERROR_INCORRECT_EPOCH: MessageFault_E
MESSAGEFAULT_ERROR_IV_INCORRECT_LENGTH: MessageFault_E
MESSAGEFAULT_ERROR_TIME_EXPIRED: MessageFault_E
MESSAGEFAULT_ERROR_NOT_PROVISIONED_WITH_IDENTITY: MessageFault_E
MESSAGEFAULT_ERROR_COULD_NOT_HASH_METADATA: MessageFault_E
MESSAGEFAULT_ERROR_TIME_TO_LIVE_TOO_LONG: MessageFault_E
MESSAGEFAULT_ERROR_REMOTE_ACCESS_DISABLED: MessageFault_E
MESSAGEFAULT_ERROR_REMOTE_SERVICE_REQUEST_NOT_SUPPORTED: MessageFault_E
SIGNATURE_TYPE_AES_GCM: SignatureType
SIGNATURE_TYPE_ECDSA: SignatureType
SIGNATURE_TYPE_PRESENT_KEY: SignatureType
SIGNATURE_TYPE_AES_GCM_TOKEN: SignatureType
SIGNATURE_TYPE_ECDSA_PERSONALIZED: SignatureType
SIGNATURE_TYPE_AES_GCM_PERSONALIZED: SignatureType
SIGNATURE_TYPE_HMAC: SignatureType
SIGNATURE_TYPE_RSA: SignatureType
SIGNATURE_TYPE_HMAC_PERSONALIZED: SignatureType
SIGNATURE_TYPE_AES_GCM_RESPONSE: SignatureType
TAG_SIGNATURE_TYPE: Tag
TAG_DOMAIN: Tag
TAG_PERSONALIZATION: Tag
TAG_EPOCH: Tag
TAG_EXPIRES_AT: Tag
TAG_COUNTER: Tag
TAG_CHALLENGE: Tag
TAG_FLAGS: Tag
TAG_REQUEST_HASH: Tag
TAG_FAULT: Tag
TAG_END: Tag
EXTERNAL_AUTH_TYPE_INVALID: ExternalAuthType
EXTERNAL_AUTH_TYPE_PRESENCE: ExternalAuthType
EXTERNAL_AUTH_TYPE_MTLS: ExternalAuthType
EXTERNAL_AUTH_TYPE_HERMES_COMMAND: ExternalAuthType
DELIVERY_CHANNEL_INVALID: DeliveryChannel
DELIVERY_CHANNEL_LOCAL_HTTPS: DeliveryChannel
DELIVERY_CHANNEL_HERMES_COMMAND: DeliveryChannel
DELIVERY_CHANNEL_BLE: DeliveryChannel
LOCAL_PARTICIPANT_INVALID: LocalParticipant
LOCAL_PARTICIPANT_INSTALLER: LocalParticipant
LOCAL_PARTICIPANT_CUSTOMER: LocalParticipant
TESLA_SERVICE_INVALID: TeslaService
TESLA_SERVICE_COMMAND: TeslaService
AUTHORIZED_CLIENT_TYPE_INVALID: AuthorizedClientType
AUTHORIZED_CLIENT_TYPE_CUSTOMER_MOBILE_APP: AuthorizedClientType
AUTHORIZED_CLIENT_TYPE_VEHICLE: AuthorizedClientType
WIFI_NETWORK_SECURITY_TYPE_INVALID: WifiNetworkSecurityType
WIFI_NETWORK_SECURITY_TYPE_NONE: WifiNetworkSecurityType
WIFI_NETWORK_SECURITY_TYPE_DYNAMIC_WEP: WifiNetworkSecurityType
WIFI_NETWORK_SECURITY_TYPE_WPA2_PERSONAL: WifiNetworkSecurityType
WIFI_NETWORK_SECURITY_TYPE_WPA2_ENTERPRISE: WifiNetworkSecurityType
NETWORK_DEVICE_STATE_INVALID: NetworkDeviceState
NETWORK_DEVICE_STATE_UNMANAGED: NetworkDeviceState
NETWORK_DEVICE_STATE_UNAVAILABLE: NetworkDeviceState
NETWORK_DEVICE_STATE_IDLE: NetworkDeviceState
NETWORK_DEVICE_STATE_ASSOCIATION: NetworkDeviceState
NETWORK_DEVICE_STATE_CONFIGURATION: NetworkDeviceState
NETWORK_DEVICE_STATE_READY: NetworkDeviceState
NETWORK_DEVICE_STATE_DISCONNECT: NetworkDeviceState
NETWORK_DEVICE_STATE_FAILURE: NetworkDeviceState
NETWORK_DEVICE_STATE_REASON_INVALID: NetworkDeviceStateReason
NETWORK_DEVICE_STATE_REASON_NONE: NetworkDeviceStateReason
NETWORK_DEVICE_STATE_REASON_CONFIG_FAILED: NetworkDeviceStateReason
NETWORK_DEVICE_STATE_REASON_DHCP_FAILED: NetworkDeviceStateReason
NETWORK_DEVICE_STATE_REASON_IP_ADDRESS_DUPLICATE: NetworkDeviceStateReason
NETWORK_DEVICE_STATE_REASON_IP_CONFIG_EXPIRED: NetworkDeviceStateReason
NETWORK_DEVICE_STATE_REASON_IP_CONFIG_UNAVAILABLE: NetworkDeviceStateReason
NETWORK_DEVICE_STATE_REASON_IP_METHOD_UNSUPPORTED: NetworkDeviceStateReason
NETWORK_DEVICE_STATE_REASON_NEW_ACTIVATION: NetworkDeviceStateReason
NETWORK_DEVICE_STATE_REASON_NO_SECRETS: NetworkDeviceStateReason
NETWORK_DEVICE_STATE_REASON_PPP_FAILED: NetworkDeviceStateReason
NETWORK_DEVICE_STATE_REASON_SSID_NOT_FOUND: NetworkDeviceStateReason
NETWORK_DEVICE_STATE_REASON_SIM_PIN_INCORRECT: NetworkDeviceStateReason
NETWORK_DEVICE_STATE_REASON_SUPPLICANT_FAILED: NetworkDeviceStateReason
NETWORK_DEVICE_STATE_REASON_REMOVED: NetworkDeviceStateReason
NETWORK_DEVICE_STATE_REASON_MODEM_FAILED: NetworkDeviceStateReason
AUTHORIZED_KEY_TYPE_INVALID: AuthorizedKeyType
AUTHORIZED_KEY_TYPE_RSA: AuthorizedKeyType
AUTHORIZED_KEY_TYPE_ECC: AuthorizedKeyType
AUTHORIZATION_ROLE_INVALID: AuthorizationRole
AUTHORIZATION_ROLE_CUSTOMER: AuthorizationRole
AUTHORIZATION_ROLE_VEHICLE: AuthorizationRole
AUTHORIZED_STATE_INVALID: AuthorizedState
AUTHORIZED_STATE_PENDING_VERIFICATION: AuthorizedState
AUTHORIZED_STATE_PENDING_VERIFICATION_TIMEOUT: AuthorizedState
AUTHORIZED_STATE_VERIFIED: AuthorizedState
AUTHORIZED_STATE_REMOVED: AuthorizedState
AUTHORIZED_VERIFICATION_TYPE_INVALID: AuthorizedVerificationType
AUTHORIZED_VERIFICATION_TYPE_PRESENCE_PROOF: AuthorizedVerificationType
AUTHORIZED_VERIFICATION_TYPE_BLE: AuthorizedVerificationType
AUTHORIZED_VERIFICATION_TYPE_SIGNED: AuthorizedVerificationType
AUTHORIZED_VERIFICATION_TYPE_HERMES_COMMAND: AuthorizedVerificationType
FILE_STORE_API_DOMAIN_INVALID: FileStoreAPIDomain
FILE_STORE_API_DOMAIN_CONFIG_JSON: FileStoreAPIDomain
FILE_STORE_API_DOMAIN_GRID_CODE_REGIONS_CSV: FileStoreAPIDomain
FILE_STORE_API_DOMAIN_CERTIFIED_INSTALLERS_CSV: FileStoreAPIDomain
FILE_STORE_API_DOMAIN_SUPERCHARGER_FILES: FileStoreAPIDomain
FILE_STORE_API_DOMAIN_OPTICASTER_FILES: FileStoreAPIDomain
FILE_STORE_API_DOMAIN_WALLBOX_CONFIG: FileStoreAPIDomain
FILE_STORE_API_DOMAIN_OCPP_CSMS_ROOT_CA: FileStoreAPIDomain

class Destination(_message.Message):
    __slots__ = ("domain", "routing_address")
    DOMAIN_FIELD_NUMBER: _ClassVar[int]
    ROUTING_ADDRESS_FIELD_NUMBER: _ClassVar[int]
    domain: Domain
    routing_address: bytes
    def __init__(self, domain: _Optional[_Union[Domain, str]] = ..., routing_address: _Optional[bytes] = ...) -> None: ...

class MessageStatus(_message.Message):
    __slots__ = ("message_fault",)
    MESSAGE_FAULT_FIELD_NUMBER: _ClassVar[int]
    message_fault: MessageFault_E
    def __init__(self, message_fault: _Optional[_Union[MessageFault_E, str]] = ...) -> None: ...

class KeyIdentity(_message.Message):
    __slots__ = ("public_key", "handle")
    PUBLIC_KEY_FIELD_NUMBER: _ClassVar[int]
    HANDLE_FIELD_NUMBER: _ClassVar[int]
    public_key: bytes
    handle: int
    def __init__(self, public_key: _Optional[bytes] = ..., handle: _Optional[int] = ...) -> None: ...

class RsaSignatureData(_message.Message):
    __slots__ = ("expires_at", "signature")
    EXPIRES_AT_FIELD_NUMBER: _ClassVar[int]
    SIGNATURE_FIELD_NUMBER: _ClassVar[int]
    expires_at: int
    signature: bytes
    def __init__(self, expires_at: _Optional[int] = ..., signature: _Optional[bytes] = ...) -> None: ...

class SignatureData(_message.Message):
    __slots__ = ("signer_identity", "rsa_data")
    SIGNER_IDENTITY_FIELD_NUMBER: _ClassVar[int]
    RSA_DATA_FIELD_NUMBER: _ClassVar[int]
    signer_identity: KeyIdentity
    rsa_data: RsaSignatureData
    def __init__(self, signer_identity: _Optional[_Union[KeyIdentity, _Mapping]] = ..., rsa_data: _Optional[_Union[RsaSignatureData, _Mapping]] = ...) -> None: ...

class RoutableMessage(_message.Message):
    __slots__ = ("to_destination", "from_destination", "protobuf_message_as_bytes", "signature_data", "signed_message_status", "request_uuid", "uuid", "flags")
    TO_DESTINATION_FIELD_NUMBER: _ClassVar[int]
    FROM_DESTINATION_FIELD_NUMBER: _ClassVar[int]
    PROTOBUF_MESSAGE_AS_BYTES_FIELD_NUMBER: _ClassVar[int]
    SIGNATURE_DATA_FIELD_NUMBER: _ClassVar[int]
    SIGNED_MESSAGE_STATUS_FIELD_NUMBER: _ClassVar[int]
    REQUEST_UUID_FIELD_NUMBER: _ClassVar[int]
    UUID_FIELD_NUMBER: _ClassVar[int]
    FLAGS_FIELD_NUMBER: _ClassVar[int]
    to_destination: Destination
    from_destination: Destination
    protobuf_message_as_bytes: bytes
    signature_data: SignatureData
    signed_message_status: MessageStatus
    request_uuid: bytes
    uuid: bytes
    flags: Flags
    def __init__(self, to_destination: _Optional[_Union[Destination, _Mapping]] = ..., from_destination: _Optional[_Union[Destination, _Mapping]] = ..., protobuf_message_as_bytes: _Optional[bytes] = ..., signature_data: _Optional[_Union[SignatureData, _Mapping]] = ..., signed_message_status: _Optional[_Union[MessageStatus, _Mapping]] = ..., request_uuid: _Optional[bytes] = ..., uuid: _Optional[bytes] = ..., flags: _Optional[_Union[Flags, str]] = ...) -> None: ...

class AuthEnvelope(_message.Message):
    __slots__ = ("payload", "externalAuth")
    PAYLOAD_FIELD_NUMBER: _ClassVar[int]
    EXTERNALAUTH_FIELD_NUMBER: _ClassVar[int]
    payload: bytes
    externalAuth: ExternalAuth
    def __init__(self, payload: _Optional[bytes] = ..., externalAuth: _Optional[_Union[ExternalAuth, _Mapping]] = ...) -> None: ...

class ExternalAuth(_message.Message):
    __slots__ = ("type",)
    TYPE_FIELD_NUMBER: _ClassVar[int]
    type: ExternalAuthType
    def __init__(self, type: _Optional[_Union[ExternalAuthType, str]] = ...) -> None: ...

class Message(_message.Message):
    __slots__ = ("message", "tail")
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    TAIL_FIELD_NUMBER: _ClassVar[int]
    message: MessageEnvelope
    tail: Tail
    def __init__(self, message: _Optional[_Union[MessageEnvelope, _Mapping]] = ..., tail: _Optional[_Union[Tail, _Mapping]] = ...) -> None: ...

class MessageEnvelope(_message.Message):
    __slots__ = ("deliveryChannel", "sender", "recipient", "common", "teg", "wc", "neuriometer", "energysitenet", "authorization", "filestore", "graphql")
    DELIVERYCHANNEL_FIELD_NUMBER: _ClassVar[int]
    SENDER_FIELD_NUMBER: _ClassVar[int]
    RECIPIENT_FIELD_NUMBER: _ClassVar[int]
    COMMON_FIELD_NUMBER: _ClassVar[int]
    TEG_FIELD_NUMBER: _ClassVar[int]
    WC_FIELD_NUMBER: _ClassVar[int]
    NEURIOMETER_FIELD_NUMBER: _ClassVar[int]
    ENERGYSITENET_FIELD_NUMBER: _ClassVar[int]
    AUTHORIZATION_FIELD_NUMBER: _ClassVar[int]
    FILESTORE_FIELD_NUMBER: _ClassVar[int]
    GRAPHQL_FIELD_NUMBER: _ClassVar[int]
    deliveryChannel: DeliveryChannel
    sender: Participant
    recipient: Participant
    common: CommonMessages
    teg: TEGMessages
    wc: WCMessages
    neuriometer: NeurioMeterMessages
    energysitenet: EnergySiteNetMessages
    authorization: AuthorizationMessages
    filestore: FileStoreMessages
    graphql: GraphQLMessages
    def __init__(self, deliveryChannel: _Optional[_Union[DeliveryChannel, str]] = ..., sender: _Optional[_Union[Participant, _Mapping]] = ..., recipient: _Optional[_Union[Participant, _Mapping]] = ..., common: _Optional[_Union[CommonMessages, _Mapping]] = ..., teg: _Optional[_Union[TEGMessages, _Mapping]] = ..., wc: _Optional[_Union[WCMessages, _Mapping]] = ..., neuriometer: _Optional[_Union[NeurioMeterMessages, _Mapping]] = ..., energysitenet: _Optional[_Union[EnergySiteNetMessages, _Mapping]] = ..., authorization: _Optional[_Union[AuthorizationMessages, _Mapping]] = ..., filestore: _Optional[_Union[FileStoreMessages, _Mapping]] = ..., graphql: _Optional[_Union[GraphQLMessages, _Mapping]] = ...) -> None: ...

class Participant(_message.Message):
    __slots__ = ("din", "teslaService", "local", "authorizedClient")
    DIN_FIELD_NUMBER: _ClassVar[int]
    TESLASERVICE_FIELD_NUMBER: _ClassVar[int]
    LOCAL_FIELD_NUMBER: _ClassVar[int]
    AUTHORIZEDCLIENT_FIELD_NUMBER: _ClassVar[int]
    din: str
    teslaService: int
    local: int
    authorizedClient: int
    def __init__(self, din: _Optional[str] = ..., teslaService: _Optional[int] = ..., local: _Optional[int] = ..., authorizedClient: _Optional[int] = ...) -> None: ...

class Tail(_message.Message):
    __slots__ = ("value",)
    VALUE_FIELD_NUMBER: _ClassVar[int]
    value: int
    def __init__(self, value: _Optional[int] = ...) -> None: ...

class CommonMessages(_message.Message):
    __slots__ = ("error_response", "get_networking_status_request", "get_networking_status_response")
    ERROR_RESPONSE_FIELD_NUMBER: _ClassVar[int]
    GET_NETWORKING_STATUS_REQUEST_FIELD_NUMBER: _ClassVar[int]
    GET_NETWORKING_STATUS_RESPONSE_FIELD_NUMBER: _ClassVar[int]
    error_response: CommonAPIErrorResponse
    get_networking_status_request: CommonAPIGetNetworkingStatusRequest
    get_networking_status_response: CommonAPIGetNetworkingStatusResponse
    def __init__(self, error_response: _Optional[_Union[CommonAPIErrorResponse, _Mapping]] = ..., get_networking_status_request: _Optional[_Union[CommonAPIGetNetworkingStatusRequest, _Mapping]] = ..., get_networking_status_response: _Optional[_Union[CommonAPIGetNetworkingStatusResponse, _Mapping]] = ...) -> None: ...

class CommonAPIErrorResponse(_message.Message):
    __slots__ = ("status",)
    STATUS_FIELD_NUMBER: _ClassVar[int]
    status: CommandStatus
    def __init__(self, status: _Optional[_Union[CommandStatus, _Mapping]] = ...) -> None: ...

class CommandStatus(_message.Message):
    __slots__ = ("code", "message")
    CODE_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    code: int
    message: str
    def __init__(self, code: _Optional[int] = ..., message: _Optional[str] = ...) -> None: ...

class CommonAPIGetNetworkingStatusRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class CommonAPIGetNetworkingStatusResponse(_message.Message):
    __slots__ = ("wifi_config", "wifi", "eth", "gsm")
    WIFI_CONFIG_FIELD_NUMBER: _ClassVar[int]
    WIFI_FIELD_NUMBER: _ClassVar[int]
    ETH_FIELD_NUMBER: _ClassVar[int]
    GSM_FIELD_NUMBER: _ClassVar[int]
    wifi_config: WifiConfig
    wifi: NetworkInterface
    eth: NetworkInterface
    gsm: NetworkInterface
    def __init__(self, wifi_config: _Optional[_Union[WifiConfig, _Mapping]] = ..., wifi: _Optional[_Union[NetworkInterface, _Mapping]] = ..., eth: _Optional[_Union[NetworkInterface, _Mapping]] = ..., gsm: _Optional[_Union[NetworkInterface, _Mapping]] = ...) -> None: ...

class WifiConfig(_message.Message):
    __slots__ = ("ssid", "security_type")
    SSID_FIELD_NUMBER: _ClassVar[int]
    SECURITY_TYPE_FIELD_NUMBER: _ClassVar[int]
    ssid: str
    security_type: WifiNetworkSecurityType
    def __init__(self, ssid: _Optional[str] = ..., security_type: _Optional[_Union[WifiNetworkSecurityType, str]] = ...) -> None: ...

class NetworkInterface(_message.Message):
    __slots__ = ("mac_address", "enabled", "active_route", "ipv4_config", "connectivity_status", "device_state", "device_state_reason")
    MAC_ADDRESS_FIELD_NUMBER: _ClassVar[int]
    ENABLED_FIELD_NUMBER: _ClassVar[int]
    ACTIVE_ROUTE_FIELD_NUMBER: _ClassVar[int]
    IPV4_CONFIG_FIELD_NUMBER: _ClassVar[int]
    CONNECTIVITY_STATUS_FIELD_NUMBER: _ClassVar[int]
    DEVICE_STATE_FIELD_NUMBER: _ClassVar[int]
    DEVICE_STATE_REASON_FIELD_NUMBER: _ClassVar[int]
    mac_address: bytes
    enabled: bool
    active_route: bool
    ipv4_config: NetworkInterfaceIPv4Config
    connectivity_status: NetworkConnectivityStatus
    device_state: NetworkDeviceState
    device_state_reason: NetworkDeviceStateReason
    def __init__(self, mac_address: _Optional[bytes] = ..., enabled: bool = ..., active_route: bool = ..., ipv4_config: _Optional[_Union[NetworkInterfaceIPv4Config, _Mapping]] = ..., connectivity_status: _Optional[_Union[NetworkConnectivityStatus, _Mapping]] = ..., device_state: _Optional[_Union[NetworkDeviceState, str]] = ..., device_state_reason: _Optional[_Union[NetworkDeviceStateReason, str]] = ...) -> None: ...

class NetworkInterfaceIPv4Config(_message.Message):
    __slots__ = ("dhcp_enabled", "address", "subnet_mask", "gateway", "dns")
    DHCP_ENABLED_FIELD_NUMBER: _ClassVar[int]
    ADDRESS_FIELD_NUMBER: _ClassVar[int]
    SUBNET_MASK_FIELD_NUMBER: _ClassVar[int]
    GATEWAY_FIELD_NUMBER: _ClassVar[int]
    DNS_FIELD_NUMBER: _ClassVar[int]
    dhcp_enabled: bool
    address: int
    subnet_mask: int
    gateway: int
    dns: _containers.RepeatedScalarFieldContainer[int]
    def __init__(self, dhcp_enabled: bool = ..., address: _Optional[int] = ..., subnet_mask: _Optional[int] = ..., gateway: _Optional[int] = ..., dns: _Optional[_Iterable[int]] = ...) -> None: ...

class NetworkConnectivityStatus(_message.Message):
    __slots__ = ("connected_physical", "connected_internet", "connected_tesla", "rssi", "snr")
    CONNECTED_PHYSICAL_FIELD_NUMBER: _ClassVar[int]
    CONNECTED_INTERNET_FIELD_NUMBER: _ClassVar[int]
    CONNECTED_TESLA_FIELD_NUMBER: _ClassVar[int]
    RSSI_FIELD_NUMBER: _ClassVar[int]
    SNR_FIELD_NUMBER: _ClassVar[int]
    connected_physical: bool
    connected_internet: bool
    connected_tesla: bool
    rssi: Rssi
    snr: _wrappers_pb2.Int32Value
    def __init__(self, connected_physical: bool = ..., connected_internet: bool = ..., connected_tesla: bool = ..., rssi: _Optional[_Union[Rssi, _Mapping]] = ..., snr: _Optional[_Union[_wrappers_pb2.Int32Value, _Mapping]] = ...) -> None: ...

class Rssi(_message.Message):
    __slots__ = ("value", "signal_strength_percent")
    VALUE_FIELD_NUMBER: _ClassVar[int]
    SIGNAL_STRENGTH_PERCENT_FIELD_NUMBER: _ClassVar[int]
    value: int
    signal_strength_percent: _wrappers_pb2.UInt32Value
    def __init__(self, value: _Optional[int] = ..., signal_strength_percent: _Optional[_Union[_wrappers_pb2.UInt32Value, _Mapping]] = ...) -> None: ...

class ControlEventSchedulingInfo(_message.Message):
    __slots__ = ("start_time", "duration_seconds", "priority")
    START_TIME_FIELD_NUMBER: _ClassVar[int]
    DURATION_SECONDS_FIELD_NUMBER: _ClassVar[int]
    PRIORITY_FIELD_NUMBER: _ClassVar[int]
    start_time: _timestamp_pb2.Timestamp
    duration_seconds: int
    priority: int
    def __init__(self, start_time: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., duration_seconds: _Optional[int] = ..., priority: _Optional[int] = ...) -> None: ...

class TEGAPISetIslandModeRequest(_message.Message):
    __slots__ = ("mode", "force")
    MODE_FIELD_NUMBER: _ClassVar[int]
    FORCE_FIELD_NUMBER: _ClassVar[int]
    mode: int
    force: bool
    def __init__(self, mode: _Optional[int] = ..., force: bool = ...) -> None: ...

class TEGAPISetIslandModeResponse(_message.Message):
    __slots__ = ("result",)
    RESULT_FIELD_NUMBER: _ClassVar[int]
    result: int
    def __init__(self, result: _Optional[int] = ...) -> None: ...

class TEGAPIDispatchBatteryPowerRequest(_message.Message):
    __slots__ = ("resume_device_mode", "real_power")
    class ResumeDeviceOperatingMode(_message.Message):
        __slots__ = ()
        def __init__(self) -> None: ...
    class RealPowerCommand(_message.Message):
        __slots__ = ("power_watts", "duration_seconds")
        POWER_WATTS_FIELD_NUMBER: _ClassVar[int]
        DURATION_SECONDS_FIELD_NUMBER: _ClassVar[int]
        power_watts: float
        duration_seconds: int
        def __init__(self, power_watts: _Optional[float] = ..., duration_seconds: _Optional[int] = ...) -> None: ...
    RESUME_DEVICE_MODE_FIELD_NUMBER: _ClassVar[int]
    REAL_POWER_FIELD_NUMBER: _ClassVar[int]
    resume_device_mode: TEGAPIDispatchBatteryPowerRequest.ResumeDeviceOperatingMode
    real_power: TEGAPIDispatchBatteryPowerRequest.RealPowerCommand
    def __init__(self, resume_device_mode: _Optional[_Union[TEGAPIDispatchBatteryPowerRequest.ResumeDeviceOperatingMode, _Mapping]] = ..., real_power: _Optional[_Union[TEGAPIDispatchBatteryPowerRequest.RealPowerCommand, _Mapping]] = ...) -> None: ...

class TEGAPIDispatchBatteryPowerResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class TEGAPIScheduleManualBackupEventRequest(_message.Message):
    __slots__ = ("scheduling_info",)
    SCHEDULING_INFO_FIELD_NUMBER: _ClassVar[int]
    scheduling_info: ControlEventSchedulingInfo
    def __init__(self, scheduling_info: _Optional[_Union[ControlEventSchedulingInfo, _Mapping]] = ...) -> None: ...

class TEGAPIScheduleManualBackupEventResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class TEGAPICancelManualBackupEventRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class TEGAPICancelManualBackupEventResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class TEGAPIGetBackupEventsRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class TEGAPIGetBackupEventsResponse(_message.Message):
    __slots__ = ("manual_backup_event", "backup_events")
    MANUAL_BACKUP_EVENT_FIELD_NUMBER: _ClassVar[int]
    BACKUP_EVENTS_FIELD_NUMBER: _ClassVar[int]
    manual_backup_event: ManualBackupEvent
    backup_events: _containers.RepeatedCompositeFieldContainer[BackupEvent]
    def __init__(self, manual_backup_event: _Optional[_Union[ManualBackupEvent, _Mapping]] = ..., backup_events: _Optional[_Iterable[_Union[BackupEvent, _Mapping]]] = ...) -> None: ...

class ManualBackupEvent(_message.Message):
    __slots__ = ("scheduling_info",)
    SCHEDULING_INFO_FIELD_NUMBER: _ClassVar[int]
    scheduling_info: ControlEventSchedulingInfo
    def __init__(self, scheduling_info: _Optional[_Union[ControlEventSchedulingInfo, _Mapping]] = ...) -> None: ...

class BackupEvent(_message.Message):
    __slots__ = ("id", "name", "scheduling_info")
    ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    SCHEDULING_INFO_FIELD_NUMBER: _ClassVar[int]
    id: str
    name: str
    scheduling_info: ControlEventSchedulingInfo
    def __init__(self, id: _Optional[str] = ..., name: _Optional[str] = ..., scheduling_info: _Optional[_Union[ControlEventSchedulingInfo, _Mapping]] = ...) -> None: ...

class TEGAPIDelayBatteryCalibrationRequest(_message.Message):
    __slots__ = ("delay_hours",)
    DELAY_HOURS_FIELD_NUMBER: _ClassVar[int]
    delay_hours: int
    def __init__(self, delay_hours: _Optional[int] = ...) -> None: ...

class TEGAPIDelayBatteryCalibrationResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class TEGAPIGetDelayBatteryCalibrationStatusRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class TEGAPIGetDelayBatteryCalibrationStatusResponse(_message.Message):
    __slots__ = ("calibration_delays_left", "calibration_delay_remaining_seconds", "max_calibration_delays")
    CALIBRATION_DELAYS_LEFT_FIELD_NUMBER: _ClassVar[int]
    CALIBRATION_DELAY_REMAINING_SECONDS_FIELD_NUMBER: _ClassVar[int]
    MAX_CALIBRATION_DELAYS_FIELD_NUMBER: _ClassVar[int]
    calibration_delays_left: int
    calibration_delay_remaining_seconds: int
    max_calibration_delays: int
    def __init__(self, calibration_delays_left: _Optional[int] = ..., calibration_delay_remaining_seconds: _Optional[int] = ..., max_calibration_delays: _Optional[int] = ...) -> None: ...

class TEGMessages(_message.Message):
    __slots__ = ("setIslandModeRequest", "setIslandModeResponse", "dispatch_battery_power_request", "dispatch_battery_power_response", "schedule_manual_backup_event_request", "schedule_manual_backup_event_response", "cancel_manual_backup_event_request", "cancel_manual_backup_event_response", "get_backup_events_request", "get_backup_events_response", "delay_battery_calibration_request", "delay_battery_calibration_response", "get_delay_battery_calibration_status_request", "get_delay_battery_calibration_status_response")
    SETISLANDMODEREQUEST_FIELD_NUMBER: _ClassVar[int]
    SETISLANDMODERESPONSE_FIELD_NUMBER: _ClassVar[int]
    DISPATCH_BATTERY_POWER_REQUEST_FIELD_NUMBER: _ClassVar[int]
    DISPATCH_BATTERY_POWER_RESPONSE_FIELD_NUMBER: _ClassVar[int]
    SCHEDULE_MANUAL_BACKUP_EVENT_REQUEST_FIELD_NUMBER: _ClassVar[int]
    SCHEDULE_MANUAL_BACKUP_EVENT_RESPONSE_FIELD_NUMBER: _ClassVar[int]
    CANCEL_MANUAL_BACKUP_EVENT_REQUEST_FIELD_NUMBER: _ClassVar[int]
    CANCEL_MANUAL_BACKUP_EVENT_RESPONSE_FIELD_NUMBER: _ClassVar[int]
    GET_BACKUP_EVENTS_REQUEST_FIELD_NUMBER: _ClassVar[int]
    GET_BACKUP_EVENTS_RESPONSE_FIELD_NUMBER: _ClassVar[int]
    DELAY_BATTERY_CALIBRATION_REQUEST_FIELD_NUMBER: _ClassVar[int]
    DELAY_BATTERY_CALIBRATION_RESPONSE_FIELD_NUMBER: _ClassVar[int]
    GET_DELAY_BATTERY_CALIBRATION_STATUS_REQUEST_FIELD_NUMBER: _ClassVar[int]
    GET_DELAY_BATTERY_CALIBRATION_STATUS_RESPONSE_FIELD_NUMBER: _ClassVar[int]
    setIslandModeRequest: TEGAPISetIslandModeRequest
    setIslandModeResponse: TEGAPISetIslandModeResponse
    dispatch_battery_power_request: TEGAPIDispatchBatteryPowerRequest
    dispatch_battery_power_response: TEGAPIDispatchBatteryPowerResponse
    schedule_manual_backup_event_request: TEGAPIScheduleManualBackupEventRequest
    schedule_manual_backup_event_response: TEGAPIScheduleManualBackupEventResponse
    cancel_manual_backup_event_request: TEGAPICancelManualBackupEventRequest
    cancel_manual_backup_event_response: TEGAPICancelManualBackupEventResponse
    get_backup_events_request: TEGAPIGetBackupEventsRequest
    get_backup_events_response: TEGAPIGetBackupEventsResponse
    delay_battery_calibration_request: TEGAPIDelayBatteryCalibrationRequest
    delay_battery_calibration_response: TEGAPIDelayBatteryCalibrationResponse
    get_delay_battery_calibration_status_request: TEGAPIGetDelayBatteryCalibrationStatusRequest
    get_delay_battery_calibration_status_response: TEGAPIGetDelayBatteryCalibrationStatusResponse
    def __init__(self, setIslandModeRequest: _Optional[_Union[TEGAPISetIslandModeRequest, _Mapping]] = ..., setIslandModeResponse: _Optional[_Union[TEGAPISetIslandModeResponse, _Mapping]] = ..., dispatch_battery_power_request: _Optional[_Union[TEGAPIDispatchBatteryPowerRequest, _Mapping]] = ..., dispatch_battery_power_response: _Optional[_Union[TEGAPIDispatchBatteryPowerResponse, _Mapping]] = ..., schedule_manual_backup_event_request: _Optional[_Union[TEGAPIScheduleManualBackupEventRequest, _Mapping]] = ..., schedule_manual_backup_event_response: _Optional[_Union[TEGAPIScheduleManualBackupEventResponse, _Mapping]] = ..., cancel_manual_backup_event_request: _Optional[_Union[TEGAPICancelManualBackupEventRequest, _Mapping]] = ..., cancel_manual_backup_event_response: _Optional[_Union[TEGAPICancelManualBackupEventResponse, _Mapping]] = ..., get_backup_events_request: _Optional[_Union[TEGAPIGetBackupEventsRequest, _Mapping]] = ..., get_backup_events_response: _Optional[_Union[TEGAPIGetBackupEventsResponse, _Mapping]] = ..., delay_battery_calibration_request: _Optional[_Union[TEGAPIDelayBatteryCalibrationRequest, _Mapping]] = ..., delay_battery_calibration_response: _Optional[_Union[TEGAPIDelayBatteryCalibrationResponse, _Mapping]] = ..., get_delay_battery_calibration_status_request: _Optional[_Union[TEGAPIGetDelayBatteryCalibrationStatusRequest, _Mapping]] = ..., get_delay_battery_calibration_status_response: _Optional[_Union[TEGAPIGetDelayBatteryCalibrationStatusResponse, _Mapping]] = ...) -> None: ...

class WCMessages(_message.Message):
    __slots__ = ("placeholder",)
    PLACEHOLDER_FIELD_NUMBER: _ClassVar[int]
    placeholder: bytes
    def __init__(self, placeholder: _Optional[bytes] = ...) -> None: ...

class NeurioMeterMessages(_message.Message):
    __slots__ = ("placeholder",)
    PLACEHOLDER_FIELD_NUMBER: _ClassVar[int]
    placeholder: bytes
    def __init__(self, placeholder: _Optional[bytes] = ...) -> None: ...

class EnergySiteNetMessages(_message.Message):
    __slots__ = ("placeholder",)
    PLACEHOLDER_FIELD_NUMBER: _ClassVar[int]
    placeholder: bytes
    def __init__(self, placeholder: _Optional[bytes] = ...) -> None: ...

class AuthorizationMessages(_message.Message):
    __slots__ = ("add_authorized_client_request", "add_authorized_client_response", "remove_authorized_client_request", "remove_authorized_client_response", "list_authorized_clients_request", "list_authorized_clients_response")
    ADD_AUTHORIZED_CLIENT_REQUEST_FIELD_NUMBER: _ClassVar[int]
    ADD_AUTHORIZED_CLIENT_RESPONSE_FIELD_NUMBER: _ClassVar[int]
    REMOVE_AUTHORIZED_CLIENT_REQUEST_FIELD_NUMBER: _ClassVar[int]
    REMOVE_AUTHORIZED_CLIENT_RESPONSE_FIELD_NUMBER: _ClassVar[int]
    LIST_AUTHORIZED_CLIENTS_REQUEST_FIELD_NUMBER: _ClassVar[int]
    LIST_AUTHORIZED_CLIENTS_RESPONSE_FIELD_NUMBER: _ClassVar[int]
    add_authorized_client_request: AuthorizationAPIAddAuthorizedClientRequest
    add_authorized_client_response: AuthorizationAPIAddAuthorizedClientResponse
    remove_authorized_client_request: AuthorizationAPIRemoveAuthorizedClientRequest
    remove_authorized_client_response: AuthorizationAPIRemoveAuthorizedClientResponse
    list_authorized_clients_request: AuthorizationAPIListAuthorizedClientsRequest
    list_authorized_clients_response: AuthorizationAPIListAuthorizedClientsResponse
    def __init__(self, add_authorized_client_request: _Optional[_Union[AuthorizationAPIAddAuthorizedClientRequest, _Mapping]] = ..., add_authorized_client_response: _Optional[_Union[AuthorizationAPIAddAuthorizedClientResponse, _Mapping]] = ..., remove_authorized_client_request: _Optional[_Union[AuthorizationAPIRemoveAuthorizedClientRequest, _Mapping]] = ..., remove_authorized_client_response: _Optional[_Union[AuthorizationAPIRemoveAuthorizedClientResponse, _Mapping]] = ..., list_authorized_clients_request: _Optional[_Union[AuthorizationAPIListAuthorizedClientsRequest, _Mapping]] = ..., list_authorized_clients_response: _Optional[_Union[AuthorizationAPIListAuthorizedClientsResponse, _Mapping]] = ...) -> None: ...

class AuthorizationRecord(_message.Message):
    __slots__ = ("type", "description", "key_type", "public_key", "roles", "state", "verification", "added_time", "identifier", "authorized_by_public_key")
    TYPE_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    KEY_TYPE_FIELD_NUMBER: _ClassVar[int]
    PUBLIC_KEY_FIELD_NUMBER: _ClassVar[int]
    ROLES_FIELD_NUMBER: _ClassVar[int]
    STATE_FIELD_NUMBER: _ClassVar[int]
    VERIFICATION_FIELD_NUMBER: _ClassVar[int]
    ADDED_TIME_FIELD_NUMBER: _ClassVar[int]
    IDENTIFIER_FIELD_NUMBER: _ClassVar[int]
    AUTHORIZED_BY_PUBLIC_KEY_FIELD_NUMBER: _ClassVar[int]
    type: AuthorizedClientType
    description: str
    key_type: AuthorizedKeyType
    public_key: bytes
    roles: _containers.RepeatedScalarFieldContainer[AuthorizationRole]
    state: AuthorizedState
    verification: AuthorizedVerificationType
    added_time: _timestamp_pb2.Timestamp
    identifier: str
    authorized_by_public_key: bytes
    def __init__(self, type: _Optional[_Union[AuthorizedClientType, str]] = ..., description: _Optional[str] = ..., key_type: _Optional[_Union[AuthorizedKeyType, str]] = ..., public_key: _Optional[bytes] = ..., roles: _Optional[_Iterable[_Union[AuthorizationRole, str]]] = ..., state: _Optional[_Union[AuthorizedState, str]] = ..., verification: _Optional[_Union[AuthorizedVerificationType, str]] = ..., added_time: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., identifier: _Optional[str] = ..., authorized_by_public_key: _Optional[bytes] = ...) -> None: ...

class AuthorizationAPIAddAuthorizedClientRequest(_message.Message):
    __slots__ = ("type", "description", "key_type", "public_key")
    TYPE_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    KEY_TYPE_FIELD_NUMBER: _ClassVar[int]
    PUBLIC_KEY_FIELD_NUMBER: _ClassVar[int]
    type: AuthorizedClientType
    description: str
    key_type: AuthorizedKeyType
    public_key: bytes
    def __init__(self, type: _Optional[_Union[AuthorizedClientType, str]] = ..., description: _Optional[str] = ..., key_type: _Optional[_Union[AuthorizedKeyType, str]] = ..., public_key: _Optional[bytes] = ...) -> None: ...

class AuthorizationAPIAddAuthorizedClientResponse(_message.Message):
    __slots__ = ("client",)
    CLIENT_FIELD_NUMBER: _ClassVar[int]
    client: AuthorizationRecord
    def __init__(self, client: _Optional[_Union[AuthorizationRecord, _Mapping]] = ...) -> None: ...

class AuthorizationAPIRemoveAuthorizedClientRequest(_message.Message):
    __slots__ = ("public_key",)
    PUBLIC_KEY_FIELD_NUMBER: _ClassVar[int]
    public_key: bytes
    def __init__(self, public_key: _Optional[bytes] = ...) -> None: ...

class AuthorizationAPIRemoveAuthorizedClientResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class AuthorizationAPIListAuthorizedClientsRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class AuthorizationAPIListAuthorizedClientsResponse(_message.Message):
    __slots__ = ("clients", "enable_line_switch_off")
    CLIENTS_FIELD_NUMBER: _ClassVar[int]
    ENABLE_LINE_SWITCH_OFF_FIELD_NUMBER: _ClassVar[int]
    clients: _containers.RepeatedCompositeFieldContainer[AuthorizationRecord]
    enable_line_switch_off: bool
    def __init__(self, clients: _Optional[_Iterable[_Union[AuthorizationRecord, _Mapping]]] = ..., enable_line_switch_off: bool = ...) -> None: ...

class GraphQLMessages(_message.Message):
    __slots__ = ("placeholder",)
    PLACEHOLDER_FIELD_NUMBER: _ClassVar[int]
    placeholder: bytes
    def __init__(self, placeholder: _Optional[bytes] = ...) -> None: ...

class FileStoreMessages(_message.Message):
    __slots__ = ("readFileRequest", "readFileResponse", "forceWriteFileRequest", "forceWriteFileResponse", "updateFileRequest", "updateFileResponse")
    READFILEREQUEST_FIELD_NUMBER: _ClassVar[int]
    READFILERESPONSE_FIELD_NUMBER: _ClassVar[int]
    FORCEWRITEFILEREQUEST_FIELD_NUMBER: _ClassVar[int]
    FORCEWRITEFILERESPONSE_FIELD_NUMBER: _ClassVar[int]
    UPDATEFILEREQUEST_FIELD_NUMBER: _ClassVar[int]
    UPDATEFILERESPONSE_FIELD_NUMBER: _ClassVar[int]
    readFileRequest: FileStoreAPIReadFileRequest
    readFileResponse: FileStoreAPIReadFileResponse
    forceWriteFileRequest: FileStoreAPIForceWriteFileRequest
    forceWriteFileResponse: FileStoreAPIForceWriteFileResponse
    updateFileRequest: FileStoreAPIUpdateFileRequest
    updateFileResponse: FileStoreAPIUpdateFileResponse
    def __init__(self, readFileRequest: _Optional[_Union[FileStoreAPIReadFileRequest, _Mapping]] = ..., readFileResponse: _Optional[_Union[FileStoreAPIReadFileResponse, _Mapping]] = ..., forceWriteFileRequest: _Optional[_Union[FileStoreAPIForceWriteFileRequest, _Mapping]] = ..., forceWriteFileResponse: _Optional[_Union[FileStoreAPIForceWriteFileResponse, _Mapping]] = ..., updateFileRequest: _Optional[_Union[FileStoreAPIUpdateFileRequest, _Mapping]] = ..., updateFileResponse: _Optional[_Union[FileStoreAPIUpdateFileResponse, _Mapping]] = ...) -> None: ...

class FileStoreAPIFile(_message.Message):
    __slots__ = ("name", "blob")
    NAME_FIELD_NUMBER: _ClassVar[int]
    BLOB_FIELD_NUMBER: _ClassVar[int]
    name: str
    blob: bytes
    def __init__(self, name: _Optional[str] = ..., blob: _Optional[bytes] = ...) -> None: ...

class FileStoreAPIReadFileRequest(_message.Message):
    __slots__ = ("domain", "name", "ifDifferentHash")
    DOMAIN_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    IFDIFFERENTHASH_FIELD_NUMBER: _ClassVar[int]
    domain: FileStoreAPIDomain
    name: str
    ifDifferentHash: bytes
    def __init__(self, domain: _Optional[_Union[FileStoreAPIDomain, str]] = ..., name: _Optional[str] = ..., ifDifferentHash: _Optional[bytes] = ...) -> None: ...

class FileStoreAPIReadFileResponse(_message.Message):
    __slots__ = ("file", "hash")
    FILE_FIELD_NUMBER: _ClassVar[int]
    HASH_FIELD_NUMBER: _ClassVar[int]
    file: FileStoreAPIFile
    hash: bytes
    def __init__(self, file: _Optional[_Union[FileStoreAPIFile, _Mapping]] = ..., hash: _Optional[bytes] = ...) -> None: ...

class FileStoreAPIUpdateFileRequest(_message.Message):
    __slots__ = ("domain", "file", "hash")
    DOMAIN_FIELD_NUMBER: _ClassVar[int]
    FILE_FIELD_NUMBER: _ClassVar[int]
    HASH_FIELD_NUMBER: _ClassVar[int]
    domain: FileStoreAPIDomain
    file: FileStoreAPIFile
    hash: bytes
    def __init__(self, domain: _Optional[_Union[FileStoreAPIDomain, str]] = ..., file: _Optional[_Union[FileStoreAPIFile, _Mapping]] = ..., hash: _Optional[bytes] = ...) -> None: ...

class FileStoreAPIUpdateFileResponse(_message.Message):
    __slots__ = ("file", "hash")
    FILE_FIELD_NUMBER: _ClassVar[int]
    HASH_FIELD_NUMBER: _ClassVar[int]
    file: FileStoreAPIFile
    hash: bytes
    def __init__(self, file: _Optional[_Union[FileStoreAPIFile, _Mapping]] = ..., hash: _Optional[bytes] = ...) -> None: ...

class FileStoreAPIForceWriteFileRequest(_message.Message):
    __slots__ = ("domain", "file")
    DOMAIN_FIELD_NUMBER: _ClassVar[int]
    FILE_FIELD_NUMBER: _ClassVar[int]
    domain: FileStoreAPIDomain
    file: FileStoreAPIFile
    def __init__(self, domain: _Optional[_Union[FileStoreAPIDomain, str]] = ..., file: _Optional[_Union[FileStoreAPIFile, _Mapping]] = ...) -> None: ...

class FileStoreAPIForceWriteFileResponse(_message.Message):
    __slots__ = ("hash",)
    HASH_FIELD_NUMBER: _ClassVar[int]
    hash: bytes
    def __init__(self, hash: _Optional[bytes] = ...) -> None: ...
