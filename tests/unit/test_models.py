import pytest
from datetime import date, datetime
from pydantic import ValidationError
from app.models import (
    Person,
    PersonCreate,
    Organization,
    OrganizationCreate,
    Domain,
    DomainCreate,
    IPAddress,
    IPAddressCreate,
    EmailAddress,
    EmailAddressCreate,
    SocialMediaProfile,
    SocialMediaProfileCreate,
    Document,
    DocumentCreate,
    Finding,
    FindingCreate,
    Source,
    SourceCreate,
    Relationship,
    RelationshipCreate,
)


class TestPerson:
    def test_create_valid_person(self):
        person = PersonCreate(
            name="John Doe",
            aliases=["JD"],
            date_of_birth=date(1990, 1, 1),
            nationality="US"
        )
        assert person.name == "John Doe"
        assert person.aliases == ["JD"]
        assert person.date_of_birth == date(1990, 1, 1)

    def test_create_person_minimal(self):
        person = PersonCreate(name="Jane Doe")
        assert person.name == "Jane Doe"
        assert person.aliases == []
        assert person.metadata == {}

    def test_person_name_required(self):
        with pytest.raises(ValidationError):
            PersonCreate(name="")

    def test_person_model_has_base_fields(self):
        person = Person(
            name="Test Person",
            id="test-id",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        assert person.id == "test-id"
        assert person.created_at is not None
        assert person.updated_at is not None


class TestOrganization:
    def test_create_valid_organization(self):
        org = OrganizationCreate(
            name="Acme Corp",
            org_type="Corporation",
            country="US"
        )
        assert org.name == "Acme Corp"
        assert org.org_type == "Corporation"

    def test_organization_name_required(self):
        with pytest.raises(ValidationError):
            OrganizationCreate(name="")


class TestDomain:
    def test_create_valid_domain(self):
        domain = DomainCreate(domain_name="example.com")
        assert domain.domain_name == "example.com"

    def test_domain_normalization(self):
        domain = Domain(domain_name="EXAMPLE.COM")
        assert domain.domain_name == "example.com"

    def test_domain_empty_fails(self):
        with pytest.raises(ValidationError):
            Domain(domain_name="")


class TestIPAddress:
    def test_create_valid_ipv4(self):
        ip = IPAddressCreate(ip_address="192.168.1.1")
        assert ip.ip_address == "192.168.1.1"

    def test_create_valid_ipv6(self):
        ip = IPAddressCreate(ip_address="2001:0db8:85a3:0000:0000:8a2e:0370:7334")
        assert ip.ip_address == "2001:0db8:85a3:0000:0000:8a2e:0370:7334"

    def test_invalid_ip_fails(self):
        with pytest.raises(ValidationError):
            IPAddress(ip_address="not.an.ip.address")


class TestEmailAddress:
    def test_create_valid_email(self):
        email = EmailAddressCreate(email="user@example.com")
        assert email.email == "user@example.com"

    def test_email_normalization(self):
        email = EmailAddress(email="USER@EXAMPLE.COM")
        assert email.email == "user@example.com"

    def test_invalid_email_fails(self):
        with pytest.raises(ValidationError):
            EmailAddress(email="notanemail")


class TestSocialMediaProfile:
    def test_create_valid_profile(self):
        profile = SocialMediaProfileCreate(
            platform="Twitter",
            username="@example"
        )
        assert profile.platform == "Twitter"
        assert profile.username == "@example"

    def test_platform_required(self):
        with pytest.raises(ValidationError):
            SocialMediaProfileCreate(username="@example")


class TestDocument:
    def test_create_valid_document(self):
        doc = DocumentCreate(
            title="Report.pdf",
            doc_type="PDF",
            url="https://example.com/report.pdf"
        )
        assert doc.title == "Report.pdf"
        assert doc.doc_type == "PDF"

    def test_document_title_required(self):
        with pytest.raises(ValidationError):
            DocumentCreate(title="")


class TestFinding:
    def test_create_valid_finding(self):
        finding = FindingCreate(
            title="Suspicious Activity",
            description="Multiple connections found",
            confidence_level="high"
        )
        assert finding.title == "Suspicious Activity"
        assert finding.confidence_level == "high"

    def test_finding_title_required(self):
        with pytest.raises(ValidationError):
            FindingCreate(description="test")


class TestSource:
    def test_create_valid_source(self):
        source = SourceCreate(
            source_name="Public Database",
            source_type="Database",
            reliability="high"
        )
        assert source.source_name == "Public Database"
        assert source.reliability == "high"

    def test_source_name_required(self):
        with pytest.raises(ValidationError):
            SourceCreate(source_type="Database")


class TestRelationship:
    def test_create_valid_relationship(self):
        rel = RelationshipCreate(
            source_entity_id="entity-1",
            target_entity_id="entity-2",
            relationship_type="OWNS"
        )
        assert rel.source_entity_id == "entity-1"
        assert rel.target_entity_id == "entity-2"
        assert rel.relationship_type == "OWNS"

    def test_self_referential_relationship_fails(self):
        with pytest.raises(ValidationError):
            RelationshipCreate(
                source_entity_id="entity-1",
                target_entity_id="entity-1",
                relationship_type="OWNS"
            )

    def test_relationship_type_required(self):
        with pytest.raises(ValidationError):
            RelationshipCreate(
                source_entity_id="entity-1",
                target_entity_id="entity-2",
                relationship_type=""
            )

