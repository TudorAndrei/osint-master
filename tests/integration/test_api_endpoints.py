import pytest
from datetime import date


class TestPersonEndpoints:
    def test_create_person(self, client):
        response = client.post(
            "/api/v1/persons",
            json={
                "name": "API Test Person",
                "aliases": ["ATP"],
                "nationality": "US"
            }
        )
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "API Test Person"
        assert data["aliases"] == ["ATP"]
        assert "id" in data
        assert "created_at" in data

    def test_get_person(self, client):
        create_response = client.post(
            "/api/v1/persons",
            json={"name": "Get Test Person"}
        )
        person_id = create_response.json()["id"]
        
        response = client.get(f"/api/v1/persons/{person_id}")
        assert response.status_code == 200
        assert response.json()["name"] == "Get Test Person"

    def test_get_nonexistent_person(self, client):
        response = client.get("/api/v1/persons/nonexistent-id")
        assert response.status_code == 404

    def test_list_persons(self, client):
        client.post("/api/v1/persons", json={"name": "Person 1"})
        client.post("/api/v1/persons", json={"name": "Person 2"})
        
        response = client.get("/api/v1/persons")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 2

    def test_update_person(self, client):
        create_response = client.post(
            "/api/v1/persons",
            json={"name": "Original Name"}
        )
        person_id = create_response.json()["id"]
        
        response = client.put(
            f"/api/v1/persons/{person_id}",
            json={"name": "Updated Name", "nationality": "CA"}
        )
        assert response.status_code == 200
        assert response.json()["name"] == "Updated Name"
        assert response.json()["nationality"] == "CA"

    def test_delete_person(self, client):
        create_response = client.post(
            "/api/v1/persons",
            json={"name": "To Delete"}
        )
        person_id = create_response.json()["id"]
        
        response = client.delete(f"/api/v1/persons/{person_id}")
        assert response.status_code == 204
        
        get_response = client.get(f"/api/v1/persons/{person_id}")
        assert get_response.status_code == 404


class TestDomainEndpoints:
    def test_create_domain(self, client):
        response = client.post(
            "/api/v1/domains",
            json={"domain_name": "test.com"}
        )
        assert response.status_code == 201
        assert response.json()["domain_name"] == "test.com"

    def test_domain_validation(self, client):
        response = client.post(
            "/api/v1/domains",
            json={"domain_name": ""}
        )
        assert response.status_code in [422, 500]


class TestIPAddressEndpoints:
    def test_create_ipv4(self, client):
        response = client.post(
            "/api/v1/ip-addresses",
            json={"ip_address": "192.168.1.1", "country": "US"}
        )
        assert response.status_code == 201
        assert response.json()["ip_address"] == "192.168.1.1"

    def test_invalid_ip_rejected(self, client):
        response = client.post(
            "/api/v1/ip-addresses",
            json={"ip_address": "not.an.ip"}
        )
        assert response.status_code in [422, 500]


class TestOrganizationEndpoints:
    def test_create_organization(self, client):
        response = client.post(
            "/api/v1/organizations",
            json={
                "name": "Test Corp",
                "org_type": "Corporation",
                "country": "US"
            }
        )
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Test Corp"
        assert data["org_type"] == "Corporation"


class TestEmailAddressEndpoints:
    def test_create_email(self, client):
        response = client.post(
            "/api/v1/email-addresses",
            json={"email": "test@example.com"}
        )
        assert response.status_code == 201
        assert response.json()["email"] == "test@example.com"


class TestSocialMediaProfileEndpoints:
    def test_create_profile(self, client):
        response = client.post(
            "/api/v1/social-media-profiles",
            json={
                "platform": "Twitter",
                "username": "@testuser"
            }
        )
        assert response.status_code == 201
        data = response.json()
        assert data["platform"] == "Twitter"
        assert data["username"] == "@testuser"


class TestDocumentEndpoints:
    def test_create_document(self, client):
        response = client.post(
            "/api/v1/documents",
            json={
                "title": "Test Document",
                "doc_type": "PDF",
                "url": "https://example.com/doc.pdf"
            }
        )
        assert response.status_code == 201
        assert response.json()["title"] == "Test Document"


class TestFindingEndpoints:
    def test_create_finding(self, client):
        response = client.post(
            "/api/v1/findings",
            json={
                "title": "Test Finding",
                "description": "Test description",
                "confidence_level": "high"
            }
        )
        assert response.status_code == 201
        assert response.json()["title"] == "Test Finding"


class TestSourceEndpoints:
    def test_create_source(self, client):
        response = client.post(
            "/api/v1/sources",
            json={
                "source_name": "Test Source",
                "source_type": "Database",
                "reliability": "high"
            }
        )
        assert response.status_code == 201
        assert response.json()["source_name"] == "Test Source"


class TestRelationshipEndpoints:
    def test_create_relationship(self, client):
        person_response = client.post(
            "/api/v1/persons",
            json={"name": "Person for Relationship"}
        )
        person_id = person_response.json()["id"]
        
        domain_response = client.post(
            "/api/v1/domains",
            json={"domain_name": "rel-domain.com"}
        )
        domain_id = domain_response.json()["id"]
        
        response = client.post(
            "/api/v1/relationships",
            json={
                "source_entity_id": person_id,
                "target_entity_id": domain_id,
                "relationship_type": "OWNS",
                "description": "Person owns domain"
            }
        )
        assert response.status_code == 201
        data = response.json()
        assert data["source_entity_id"] == person_id
        assert data["target_entity_id"] == domain_id
        assert data["relationship_type"] == "OWNS"

    def test_get_relationships(self, client):
        person_response = client.post(
            "/api/v1/persons",
            json={"name": "Person for Rel Query"}
        )
        person_id = person_response.json()["id"]
        
        domain_response = client.post(
            "/api/v1/domains",
            json={"domain_name": "query-domain.com"}
        )
        domain_id = domain_response.json()["id"]
        
        client.post(
            "/api/v1/relationships",
            json={
                "source_entity_id": person_id,
                "target_entity_id": domain_id,
                "relationship_type": "OWNS"
            }
        )
        
        response = client.get(f"/api/v1/relationships?entity_id={person_id}")
        assert response.status_code == 200
        relationships = response.json()
        assert len(relationships) >= 1
        assert relationships[0]["source_entity_id"] == person_id

    def test_self_referential_relationship_rejected(self, client):
        person_response = client.post(
            "/api/v1/persons",
            json={"name": "Person for Self Ref"}
        )
        person_id = person_response.json()["id"]
        
        response = client.post(
            "/api/v1/relationships",
            json={
                "source_entity_id": person_id,
                "target_entity_id": person_id,
                "relationship_type": "OWNS"
            }
        )
        assert response.status_code == 422


class TestHealthEndpoint:
    def test_health_check(self, client):
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert data["status"] == "healthy"
        assert data["database"] == "connected"

