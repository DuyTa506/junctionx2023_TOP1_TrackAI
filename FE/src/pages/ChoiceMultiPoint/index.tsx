import React, { useState } from 'react';

const ChoiceMultiPoint = () => {
  const [positions, setPositions] = useState<any>([]);

  const handleOnClick = (event) => {
    const imageRect = event.target.getBoundingClientRect();
    const mouseX = event.clientX - imageRect.left;
    const mouseY = event.clientY - imageRect.top;
    const newPositions = [...positions, { x: mouseX, y: mouseY }];
    setPositions(newPositions);
  };

  return (
    <div>
      <img
        src={"../../assets/imgs/sdf.png"}
        alt="Example Image"
        style={{ width: '300px', height: '200px', border: '1px solid black' }}
        onClick={handleOnClick}
      />
      <p>Click on the image to get positions:</p>
      {positions.map((position, index) => (
        <p key={index}>Position {index + 1}: X: {position.x}, Y: {position.y}</p>
      ))}
    </div>
  );
};

export default ChoiceMultiPoint;
