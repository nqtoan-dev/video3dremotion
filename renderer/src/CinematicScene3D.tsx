import React, { useMemo } from "react";
import { ThreeCanvas } from "@remotion/three";
import { useCurrentFrame, useVideoConfig, interpolate } from "remotion";
import * as THREE from "three";

interface CinematicScene3DProps {
  particlePreset: "warm_dust" | "mist" | "embers" | "none" | string;
  cameraMotion: string;
}

const VolumetricParticles: React.FC<{
  preset: string;
  frame: number;
  durationInFrames: number;
}> = ({ preset, frame, durationInFrames }) => {
  const count = preset === "none" ? 0 : 180;

  const particles = useMemo(() => {
    const positions = new Float32Array(count * 3);
    for (let i = 0; i < count; i++) {
      const seed1 = Math.sin(i * 12.9898) * 43758.5453;
      const seed2 = Math.sin(i * 78.233) * 43758.5453;
      const seed3 = Math.sin(i * 45.164) * 43758.5453;
      positions[i * 3] = ((seed1 - Math.floor(seed1)) - 0.5) * 16;
      positions[i * 3 + 1] = ((seed2 - Math.floor(seed2)) - 0.5) * 9;
      positions[i * 3 + 2] = ((seed3 - Math.floor(seed3)) - 0.5) * 8;
    }
    return positions;
  }, [count]);

  if (count === 0) return null;

  const driftY = interpolate(frame, [0, durationInFrames], [0, 0.85]);
  const driftX = Math.sin(frame * 0.03) * 0.25;

  const color =
    preset === "embers"
      ? "#ff7b29"
      : preset === "mist"
      ? "#cfe8ff"
      : "#ffe5b4";

  return (
    <points position={[driftX, driftY, 0]}>
      <bufferGeometry>
        <bufferAttribute
          attach="attributes-position"
          count={particles.length / 3}
          array={particles}
          itemSize={3}
        />
      </bufferGeometry>
      <pointsMaterial
        size={preset === "mist" ? 0.14 : 0.065}
        color={color}
        transparent
        opacity={preset === "mist" ? 0.22 : 0.55}
        blending={THREE.AdditiveBlending}
        depthWrite={false}
      />
    </points>
  );
};

export const CinematicScene3D: React.FC<CinematicScene3DProps> = ({
  particlePreset,
}) => {
  const frame = useCurrentFrame();
  const { width, height, durationInFrames } = useVideoConfig();

  const camZ = interpolate(frame, [0, durationInFrames], [6.0, 5.15], {
    extrapolateRight: "clamp",
  });
  const swayX = Math.sin(frame * 0.045) * 0.08;
  const swayY = Math.cos(frame * 0.035) * 0.05;

  return (
    <ThreeCanvas
      width={width}
      height={height}
      style={{ position: "absolute", inset: 0, pointerEvents: "none" }}
      camera={{ position: [swayX, swayY, camZ], fov: 42 }}
    >
      <ambientLight intensity={0.6} />
      <directionalLight position={[5, 8, 4]} intensity={1.4} color="#ffdcb4" />
      <VolumetricParticles
        preset={particlePreset}
        frame={frame}
        durationInFrames={durationInFrames}
      />
    </ThreeCanvas>
  );
};
