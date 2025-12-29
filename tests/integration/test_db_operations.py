from app.db import (
    create_entity,
    create_relationship,
    delete_entity,
    get_entities_by_label,
    get_entity,
    get_relationships,
    update_entity,
)
from app.models import Domain, IPAddress, Person


class TestEntityOperations:
    def test_create_and_retrieve_person(self, test_db) -> None:
        person = Person(
            name="Test Person",
            aliases=["TP"],
            nationality="US",
        )
        entity_id = create_entity(test_db, "Person", person)

        retrieved = get_entity(test_db, "Person", entity_id)
        assert retrieved is not None
        assert retrieved["name"] == "Test Person"
        assert retrieved["aliases"] == ["TP"]
        assert retrieved["nationality"] == "US"
        assert retrieved["id"] == entity_id

    def test_list_entities(self, test_db) -> None:
        person1 = Person(name="Person 1")
        person2 = Person(name="Person 2")

        create_entity(test_db, "Person", person1)
        create_entity(test_db, "Person", person2)

        entities = get_entities_by_label(test_db, "Person")
        assert len(entities) >= 2
        names = [e["name"] for e in entities]
        assert "Person 1" in names
        assert "Person 2" in names

    def test_update_entity(self, test_db) -> None:
        person = Person(name="Original Name")
        entity_id = create_entity(test_db, "Person", person)

        updates = {"name": "Updated Name", "nationality": "CA"}
        updated = update_entity(test_db, "Person", entity_id, updates)

        assert updated is not None
        assert updated["name"] == "Updated Name"
        assert updated["nationality"] == "CA"
        assert updated["id"] == entity_id

    def test_delete_entity(self, test_db) -> None:
        person = Person(name="To Delete")
        entity_id = create_entity(test_db, "Person", person)

        deleted = delete_entity(test_db, "Person", entity_id)
        assert deleted is True

        retrieved = get_entity(test_db, "Person", entity_id)
        assert retrieved is None

    def test_get_nonexistent_entity(self, test_db) -> None:
        result = get_entity(test_db, "Person", "nonexistent-id")
        assert result is None


class TestDomainOperations:
    def test_create_domain(self, test_db) -> None:
        domain = Domain(domain_name="example.com")
        entity_id = create_entity(test_db, "Domain", domain)

        retrieved = get_entity(test_db, "Domain", entity_id)
        assert retrieved["domain_name"] == "example.com"

    def test_domain_normalization_stored(self, test_db) -> None:
        domain = Domain(domain_name="EXAMPLE.COM")
        entity_id = create_entity(test_db, "Domain", domain)

        retrieved = get_entity(test_db, "Domain", entity_id)
        assert retrieved["domain_name"] == "example.com"


class TestIPAddressOperations:
    def test_create_ipv4(self, test_db) -> None:
        ip = IPAddress(ip_address="192.168.1.1", country="US")
        entity_id = create_entity(test_db, "IPAddress", ip)

        retrieved = get_entity(test_db, "IPAddress", entity_id)
        assert retrieved["ip_address"] == "192.168.1.1"
        assert retrieved["country"] == "US"

    def test_create_ipv6(self, test_db) -> None:
        ip = IPAddress(ip_address="2001:0db8:85a3:0000:0000:8a2e:0370:7334")
        entity_id = create_entity(test_db, "IPAddress", ip)

        retrieved = get_entity(test_db, "IPAddress", entity_id)
        assert retrieved["ip_address"] == "2001:0db8:85a3:0000:0000:8a2e:0370:7334"


class TestRelationshipOperations:
    def test_create_relationship(self, test_db) -> None:
        person = Person(name="Person A")
        domain = Domain(domain_name="example.com")

        person_id = create_entity(test_db, "Person", person)
        domain_id = create_entity(test_db, "Domain", domain)

        rel_id = create_relationship(
            test_db,
            person_id,
            domain_id,
            "OWNS",
            {"description": "Person owns domain"},
        )

        assert rel_id is not None

    def test_get_relationships(self, test_db) -> None:
        person = Person(name="Person B")
        domain1 = Domain(domain_name="domain1.com")
        domain2 = Domain(domain_name="domain2.com")

        person_id = create_entity(test_db, "Person", person)
        domain1_id = create_entity(test_db, "Domain", domain1)
        domain2_id = create_entity(test_db, "Domain", domain2)

        create_relationship(test_db, person_id, domain1_id, "OWNS")
        create_relationship(test_db, person_id, domain2_id, "OWNS")

        relationships = get_relationships(test_db, person_id)
        assert len(relationships) == 2

        target_ids = [r["target_entity_id"] for r in relationships]
        assert domain1_id in target_ids
        assert domain2_id in target_ids

    def test_relationship_bidirectional_query(self, test_db) -> None:
        person = Person(name="Person C")
        domain = Domain(domain_name="domain3.com")

        person_id = create_entity(test_db, "Person", person)
        domain_id = create_entity(test_db, "Domain", domain)

        create_relationship(test_db, person_id, domain_id, "OWNS")

        person_rels = get_relationships(test_db, person_id)
        domain_rels = get_relationships(test_db, domain_id)

        assert len(person_rels) == 1
        assert len(domain_rels) == 1
        assert person_rels[0]["source_entity_id"] == person_id
        assert domain_rels[0]["target_entity_id"] == domain_id
