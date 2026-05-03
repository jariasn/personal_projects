import React, { useState, useRef } from 'react';
import { Canvas } from '@react-three/fiber';
import { OrbitControls, Html } from '@react-three/drei';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Download } from 'lucide-react';

const hsvToRgb = (h, s, v) => {
  h = h / 360;
  let r, g, b;
  const i = Math.floor(h * 6);
  const f = h * 6 - i;
  const p = v * (1 - s);
  const q = v * (1 - f * s);
  const t = v * (1 - (1 - f) * s);

  switch (i % 6) {
    case 0: r = v; g = t; b = p; break;
    case 1: r = q; g = v; b = p; break;
    case 2: r = p; g = v; b = t; break;
    case 3: r = p; g = q; b = v; break;
    case 4: r = t; g = p; b = v; break;
    case 5: r = v; g = p; b = q; break;
  }

  return [r, g, b].map(x => Math.round(x * 255));
};

const ColorPoint = ({ position, color, onClick, selected, isCustom }) => (
  <mesh position={position} onClick={onClick}>
    <sphereGeometry args={[isCustom ? 0.03 : 0.015, 16, 16]} />
    <meshStandardMaterial 
      color={color}
      emissive={selected ? "#ffffff" : isCustom ? color : "#000000"}
      emissiveIntensity={selected ? 0.5 : isCustom ? 0.3 : 0}
    />
  </mesh>
);

const ColorSpaceClusterEditor = () => {
  const [points, setPoints] = useState([]);
  const [customPoints, setCustomPoints] = useState([]);
  const [clusters, setClusters] = useState({});
  const [currentCluster, setCurrentCluster] = useState("");
  const [selectedPoints, setSelectedPoints] = useState([]);

  const generatePoints = () => {
    const newPoints = [];
    for (let h = 0; h < 360; h += 5) {
      for (let s = 0; s <= 1; s += 0.05) {
        for (let v = 0; v <= 1; v += 0.05) {
          const [r, g, b] = hsvToRgb(h, s, v);
          const radius = s;
          const angle = (h * Math.PI) / 180;
          newPoints.push({
            hsv: [h, s, v],
            position: [
              radius * Math.cos(angle),
              v - 0.5,
              radius * Math.sin(angle)
            ],
            color: `rgb(${r},${g},${b})`
          });
        }
      }
    }
    setPoints(newPoints);
  };

  const handleCanvasClick = (event) => {
    if (event.buttons !== 1 || event.object) return;

    const point = event.point;
    const x = point.x;
    const y = point.y + 0.5;
    const z = point.z;

    const h = ((Math.atan2(z, x) * 180 / Math.PI) + 360) % 360;
    const s = Math.sqrt(x * x + z * z);
    const v = Math.max(0, Math.min(1, y));

    const [r, g, b] = hsvToRgb(h, s, v);
    const color = `rgb(${r},${g},${b})`;

    const newPoint = {
      hsv: [h, s, v],
      position: [x, y - 0.5, z],
      color: color,
      isCustom: true
    };

    setCustomPoints(prev => [...prev, newPoint]);
    setSelectedPoints(prev => [...prev, newPoint]);
  };

  const handlePointClick = (point, event) => {
    event.stopPropagation();
    if (!currentCluster) return;

    const isSelected = selectedPoints.some(p => 
      p.position[0] === point.position[0] && 
      p.position[1] === point.position[1] && 
      p.position[2] === point.position[2]
    );

    if (isSelected) {
      setSelectedPoints(prev => prev.filter(p => 
        p.position[0] !== point.position[0] || 
        p.position[1] !== point.position[1] || 
        p.position[2] !== point.position[2]
      ));
    } else {
      setSelectedPoints(prev => [...prev, point]);
    }
  };

  const saveCluster = () => {
    if (!currentCluster || selectedPoints.length === 0) return;

    setClusters(prev => ({
      ...prev,
      [currentCluster]: selectedPoints.map(p => ({
        hsv: p.hsv,
        rgb: p.color,
        position: p.position
      }))
    }));

    setSelectedPoints([]);
    setCurrentCluster("");
  };

  const exportClusters = () => {
    const exportData = {
      clusters: clusters,
      metadata: {
        exportDate: new Date().toISOString(),
        totalClusters: Object.keys(clusters).length,
        pointsPerCluster: Object.entries(clusters).map(([name, points]) => ({
          cluster: name,
          count: points.length
        }))
      }
    };

    const dataStr = JSON.stringify(exportData, null, 2);
    const dataBlob = new Blob([dataStr], { type: 'application/json' });
    const url = URL.createObjectURL(dataBlob);
    const link = document.createElement('a');
    link.href = url;
    link.download = 'color-clusters.json';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  };

  return (
    <div className="w-full h-screen flex flex-col">
      <div className="flex gap-4 p-4 bg-gray-900 text-white">
        <Button onClick={generatePoints} className="w-40">
          Generate Points
        </Button>
        <Input
          placeholder="Enter cluster name"
          value={currentCluster}
          onChange={(e) => setCurrentCluster(e.target.value)}
          className="w-48"
        />
        <Button 
          onClick={saveCluster} 
          disabled={!currentCluster || selectedPoints.length === 0}
          className="w-40"
        >
          Save Cluster
        </Button>
        <Button 
          onClick={exportClusters} 
          disabled={Object.keys(clusters).length === 0}
          className="w-40"
        >
          <Download className="mr-2 h-4 w-4" />
          Export JSON
        </Button>
      </div>

      <div className="h-[800px] border rounded-lg overflow-hidden bg-gray-100">
        <Canvas 
          camera={{ position: [2, 2, 2], fov: 50 }}
          onPointerMissed={handleCanvasClick}
        >
          <ambientLight intensity={1} />
          <pointLight position={[10, 10, 10]} intensity={1.5} />
          <OrbitControls makeDefault />

          <group>
            <Html position={[1.2, 0, 0]}>
              <div className="text-sm font-bold">Hue</div>
            </Html>
            <Html position={[0, 1.2, 0]}>
              <div className="text-sm font-bold">Value</div>
            </Html>
            <Html position={[0, 0, 1.2]}>
              <div className="text-sm font-bold">Saturation</div>
            </Html>
          </group>

          {points.map((point, i) => (
            <ColorPoint
              key={`gen-${i}`}
              position={point.position}
              color={point.color}
              onClick={(e) => handlePointClick(point, e)}
              selected={selectedPoints.includes(point)}
              isCustom={false}
            />
          ))}

          {customPoints.map((point, i) => (
            <ColorPoint
              key={`custom-${i}`}
              position={point.position}
              color={point.color}
              onClick={(e) => handlePointClick(point, e)}
              selected={selectedPoints.includes(point)}
              isCustom={true}
            />
          ))}
        </Canvas>
      </div>

      <div className="mt-4">
        <h3 className="font-semibold mb-2">Saved Clusters:</h3>
        <div className="space-y-2">
          {Object.entries(clusters).map(([name, points]) => (
            <div key={name} className="flex items-center gap-2 p-2 bg-gray-100 rounded">
              <span className="font-medium">{name}:</span>
              <span>{points.length} points</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default ColorSpaceClusterEditor;