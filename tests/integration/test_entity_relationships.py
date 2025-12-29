import pytest


class TestEntityRelationshipIntegration:
    def test_person_domain_relationship_flow(self, client):
        person_response = client.post(
            "/api/v1/persons",
            json={
                "name": "Integration Test Person",
                "nationality": "US"
            }
        )
        person_id = person_response.json()["id"]
        
        domain_response = client.post(
            "/api/v1/domains",
            json={
                "domain_name": "integration-test.com",
                "registrar": "Test Registrar"
            }
        )
        domain_id = domain_response.json()["id"]
        
        rel_response = client.post(
            "/api/v1/relationships",
            json={
                "source_entity_id": person_id,
                "target_entity_id": domain_id,
                "relationship_type": "OWNS",
                "description": "Person owns domain"
            }
        )
        assert rel_response.status_code == 201
        
        person_rels = client.get(f"/api/v1/relationships?entity_id={person_id}")
        assert person_rels.status_code == 200
        assert len(person_rels.json()) >= 1
        
        domain_rels = client.get(f"/api/v1/relationships?entity_id={domain_id}")
        assert domain_rels.status_code == 200
        assert len(domain_rels.json()) >= 1

    def test_multiple_relationships_for_entity(self, client):
        person_response = client.post(
            "/api/v1/persons",
            json={"name": "Multi-Rel Person"}
        )
        person_id = person_response.json()["id"]
        
        domain1_response = client.post(
            "/api/v1/domains",
            json={"domain_name": "domain1.com"}
        )
        domain1_id = domain1_response.json()["id"]
        
        domain2_response = client.post(
            "/api/v1/domains",
            json={"domain_name": "domain2.com"}
        )
        domain2_id = domain2_response.json()["id"]
        
        email_response = client.post(
            "/api/v1/email-addresses",
            json={"email": "person@domain1.com"}
        )
        email_id = email_response.json()["id"]
        
        client.post(
            "/api/v1/relationships",
            json={
                "source_entity_id": person_id,
                "target_entity_id": domain1_id,
                "relationship_type": "OWNS"
            }
        )
        
        client.post(
            "/api/v1/relationships",
            json={
                "source_entity_id": person_id,
                "target_entity_id": domain2_id,
                "relationship_type": "OWNS"
            }
        )
        
        client.post(
            "/api/v1/relationships",
            json={
                "source_entity_id": person_id,
                "target_entity_id": email_id,
                "relationship_type": "USES"
            }
        )
        
        relationships = client.get(f"/api/v1/relationships?entity_id={person_id}")
        assert relationships.status_code == 200
        rels = relationships.json()
        assert len(rels) == 3
        
        rel_types = [r["relationship_type"] for r in rels]
        assert "OWNS" in rel_types
        assert "USES" in rel_types

    def test_finding_with_related_entities(self, client):
        person_response = client.post(
            "/api/v1/persons",
            json={"name": "Finding Person"}
        )
        person_id = person_response.json()["id"]
        
        domain_response = client.post(
            "/api/v1/domains",
            json={"domain_name": "finding-domain.com"}
        )
        domain_id = domain_response.json()["id"]
        
        finding_response = client.post(
            "/api/v1/findings",
            json={
                "title": "Suspicious Connection",
                "description": "Person connected to suspicious domain",
                "confidence_level": "high",
                "related_entity_ids": [person_id, domain_id],
                "tags": ["suspicious", "network"]
            }
        )
        assert finding_response.status_code == 201
        finding = finding_response.json()
        assert len(finding["related_entity_ids"]) == 2
        assert person_id in finding["related_entity_ids"]
        assert domain_id in finding["related_entity_ids"]

    def test_organization_person_relationship(self, client):
        org_response = client.post(
            "/api/v1/organizations",
            json={
                "name": "Test Organization",
                "org_type": "Corporation"
            }
        )
        org_id = org_response.json()["id"]
        
        person_response = client.post(
            "/api/v1/persons",
            json={"name": "Org Employee"}
        )
        person_id = person_response.json()["id"]
        
        rel_response = client.post(
            "/api/v1/relationships",
            json={
                "source_entity_id": person_id,
                "target_entity_id": org_id,
                "relationship_type": "EMPLOYED_BY"
            }
        )
        assert rel_response.status_code == 201
        
        person_rels = client.get(f"/api/v1/relationships?entity_id={person_id}")
        org_rels = client.get(f"/api/v1/relationships?entity_id={org_id}")
        
        assert len(person_rels.json()) >= 1
        assert len(org_rels.json()) >= 1

