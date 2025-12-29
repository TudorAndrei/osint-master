## ADDED Requirements

### Requirement: Person Entity Model
The system SHALL provide a Pydantic model for Person entities with fields for name, aliases, date of birth, nationality, and metadata.

#### Scenario: Valid person creation
- **WHEN** a Person model is instantiated with valid data
- **THEN** the model SHALL validate successfully
- **AND** all required fields SHALL be present

#### Scenario: Invalid person data rejection
- **WHEN** a Person model is instantiated with invalid data
- **THEN** the model SHALL raise a validation error
- **AND** the error SHALL indicate which fields are invalid

### Requirement: Organization Entity Model
The system SHALL provide a Pydantic model for Organization entities with fields for name, aliases, organization type, registration details, and metadata.

#### Scenario: Valid organization creation
- **WHEN** an Organization model is instantiated with valid data
- **THEN** the model SHALL validate successfully

### Requirement: Domain Entity Model
The system SHALL provide a Pydantic model for Domain entities with fields for domain name, registration date, registrar, and metadata.

#### Scenario: Valid domain creation
- **WHEN** a Domain model is instantiated with valid domain name
- **THEN** the model SHALL validate successfully
- **AND** the domain name SHALL be normalized

### Requirement: IPAddress Entity Model
The system SHALL provide a Pydantic model for IPAddress entities with fields for IP address (IPv4 or IPv6), geolocation data, and metadata.

#### Scenario: Valid IPv4 address
- **WHEN** an IPAddress model is instantiated with valid IPv4 address
- **THEN** the model SHALL validate successfully

#### Scenario: Valid IPv6 address
- **WHEN** an IPAddress model is instantiated with valid IPv6 address
- **THEN** the model SHALL validate successfully

#### Scenario: Invalid IP address rejection
- **WHEN** an IPAddress model is instantiated with invalid IP format
- **THEN** the model SHALL raise a validation error

### Requirement: EmailAddress Entity Model
The system SHALL provide a Pydantic model for EmailAddress entities with fields for email address, associated domains, and metadata.

#### Scenario: Valid email creation
- **WHEN** an EmailAddress model is instantiated with valid email format
- **THEN** the model SHALL validate successfully

### Requirement: SocialMediaProfile Entity Model
The system SHALL provide a Pydantic model for SocialMediaProfile entities with fields for platform, username, profile URL, and metadata.

#### Scenario: Valid social media profile creation
- **WHEN** a SocialMediaProfile model is instantiated with valid platform and username
- **THEN** the model SHALL validate successfully

### Requirement: Document Entity Model
The system SHALL provide a Pydantic model for Document entities with fields for title, document type, file path or URL, content hash, and metadata.

#### Scenario: Valid document creation
- **WHEN** a Document model is instantiated with valid document data
- **THEN** the model SHALL validate successfully

### Requirement: Finding Entity Model
The system SHALL provide a Pydantic model for Finding entities with fields for title, description, confidence level, related entities, and metadata.

#### Scenario: Valid finding creation
- **WHEN** a Finding model is instantiated with valid finding data
- **THEN** the model SHALL validate successfully

### Requirement: Source Entity Model
The system SHALL provide a Pydantic model for Source entities with fields for source name, source type, URL, collection date, and metadata.

#### Scenario: Valid source creation
- **WHEN** a Source model is instantiated with valid source data
- **THEN** the model SHALL validate successfully

### Requirement: Relationship Entity Model
The system SHALL provide a Pydantic model for Relationship entities with fields for source entity ID, target entity ID, relationship type, and metadata.

#### Scenario: Valid relationship creation
- **WHEN** a Relationship model is instantiated with valid source and target entity IDs
- **THEN** the model SHALL validate successfully

#### Scenario: Self-referential relationship prevention
- **WHEN** a Relationship model is instantiated with same source and target ID
- **THEN** the model SHALL raise a validation error

### Requirement: Base Entity Model
The system SHALL provide a base Pydantic model with common fields (ID, created_at, updated_at, metadata) that all entity models inherit from.

#### Scenario: Base fields inheritance
- **WHEN** any entity model inherits from the base model
- **THEN** the entity SHALL automatically include ID, timestamps, and metadata fields

