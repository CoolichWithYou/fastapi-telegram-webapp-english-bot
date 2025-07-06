// import {Canvas} from '@react-three/fiber';
//
// import {OrbitControls, useGLTF} from '@react-three/drei';
//
//
// const EarthCanvas = () => {
//
//     const earth = useGLTF('/assets/reworked.gltf');
//
//
//     return (
//
//         <Canvas className="cursor-pointer" frameloop="demand"
//                 camera={{position: [-4, 3, 6], fov: 90, near: 5.2, far: 500}}>
//   <ambientLight intensity={0.5} />
//
//             <OrbitControls autoRotate enableZoom={false} maxPolarAngle={Math.PI / 2} minPolarAngle={Math.PI / 2}
//                            enablePan={false}/>
//
//             <primitive object={earth.scene} scale={5}/>
//
//            <ambientLight intensity={0.5} />
//         </Canvas>
//
//     );
//
// };
//
//
// export default EarthCanvas;