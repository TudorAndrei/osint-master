import { useEffect, useMemo } from "react";
import { MapContainer, TileLayer, Marker, Popup, useMap } from "react-leaflet";
import "leaflet/dist/leaflet.css";
import L from "leaflet";
import type { GraphNode } from "@/api/types";
import icon from "leaflet/dist/images/marker-icon.png";
import iconShadow from "leaflet/dist/images/marker-shadow.png";

const DefaultIcon = L.icon({
  iconUrl: icon,
  shadowUrl: iconShadow,
  iconSize: [25, 41],
  iconAnchor: [12, 41],
});

L.Marker.prototype.options.icon = DefaultIcon;

interface EntityMapProps {
  nodes: GraphNode[];
  onSelect: (entityId: string) => void;
  selectedEntityId: string | null;
}

function MapUpdater({ nodes, selectedEntityId }: { nodes: GraphNode[]; selectedEntityId: string | null }) {
  const map = useMap();

  const mapNodes = useMemo(() => {
    return nodes.filter((node) => {
      const lat = parseFloat(node.properties.latitude?.[0] || "");
      const lng = parseFloat(node.properties.longitude?.[0] || "");
      return !isNaN(lat) && !isNaN(lng);
    });
  }, [nodes]);

  useEffect(() => {
    if (mapNodes.length === 0) return;

    if (selectedEntityId) {
      const selectedNode = mapNodes.find((n) => n.id === selectedEntityId);
      if (selectedNode) {
        const lat = parseFloat(selectedNode.properties.latitude?.[0] || "0");
        const lng = parseFloat(selectedNode.properties.longitude?.[0] || "0");
        if (!isNaN(lat) && !isNaN(lng)) {
          map.flyTo([lat, lng], 13);
          return;
        }
      }
    }

    const bounds = L.latLngBounds(
      mapNodes.map((n) => {
        const lat = parseFloat(n.properties.latitude?.[0] || "0");
        const lng = parseFloat(n.properties.longitude?.[0] || "0");
        return [lat, lng];
      })
    );

    if (bounds.isValid()) {
      map.fitBounds(bounds, { padding: [50, 50] });
    }
  }, [mapNodes, map, selectedEntityId]);

  return null;
}

export default function EntityMap({ nodes, onSelect, selectedEntityId }: EntityMapProps) {
  const mapNodes = useMemo(() => {
    const filtered = nodes.filter((node) => {
      const lat = parseFloat(node.properties.latitude?.[0] || "");
      const lng = parseFloat(node.properties.longitude?.[0] || "");
      return !isNaN(lat) && !isNaN(lng);
    });
    console.log("EntityMap: filtered nodes with location:", filtered);
    return filtered;
  }, [nodes]);

  const defaultCenter: [number, number] = [20, 0];

  return (
    <div className="flex-1 h-full w-full rounded-md border overflow-hidden relative z-0 flex flex-col">
      <MapContainer center={defaultCenter} zoom={2} className="flex-1 w-full h-full">
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />
        <MapUpdater nodes={mapNodes} selectedEntityId={selectedEntityId} />
        {mapNodes.map((node) => {
          const lat = parseFloat(node.properties.latitude?.[0] || "0");
          const lng = parseFloat(node.properties.longitude?.[0] || "0");
          const label = node.properties.name?.[0] || node.label || node.id;

          return (
            <Marker
              key={node.id}
              position={[lat, lng]}
              eventHandlers={{
                click: () => onSelect(node.id),
              }}
            >
              <Popup>
                <div className="text-sm">
                  <p className="font-semibold">{label}</p>
                  <p className="text-xs text-muted-foreground">{node.schema}</p>
                </div>
              </Popup>
            </Marker>
          );
        })}
      </MapContainer>
    </div>
  );
}
