import React, { useRef, useState, useEffect } from "react";

import Images from "../../sdf.png";

function Demo() {
  const canvasRef = useRef(null);

  const [positions, setPositions] = useState([]);
  const [prevPoint, setPrevPoint] = useState(undefined);
  const [curPoint, setCurPoint] = useState(undefined);

  const handleOnClick = (event) => {
    const imageRect = event.target.getBoundingClientRect();
    const mouseX = event.clientX - imageRect.left;
    const mouseY = event.clientY - imageRect.top;
    setPrevPoint(curPoint);
    setCurPoint({ x: mouseX, y: mouseY });
    const newPositions = [...positions, { x: mouseX, y: mouseY }];
    setPositions(newPositions);
  };

  const drawLine = (ctx, prevPoint, curPoint) => {
    if (prevPoint) {
      ctx.strokeStyle = "black";
      ctx.lineWidth = 2;

      // Vẽ đường thẳng
      ctx.beginPath();
      ctx.moveTo(prevPoint.x, prevPoint.y); // Điểm bắt đầu (x, y)
      ctx.lineTo(curPoint.x, curPoint.y); // Điểm kết thúc (x, y)
      ctx.stroke(); // Hoàn thành vẽ đường thẳng
    }
  };

  useEffect(() => {
    const canvas = canvasRef.current;
    const ctx = canvas.getContext("2d");

    // Load the image
    const img = new Image();
    img.src = Images; // Replace 'image.jpg' with the URL of your image file

    // Draw the image on the canvas when it's loaded
    img.onload = () => {
      ctx.drawImage(img, 0, 0); // Draws the image at (0, 0) coordinates on the canvas
      // Thiết lập thuộc tính cho đường thẳng
      drawLine(ctx, prevPoint, curPoint);
    };
  }, [positions]);

  return (
    <div>
      <canvas
        ref={canvasRef}
        width={500}
        height={300}
        onClick={handleOnClick}
      ></canvas>
      <p>Click on the image to get positions:</p>
      {positions.map((position, index) => (
        <p key={index}>
          Position {index + 1}: X: {position.x}, Y: {position.y}
        </p>
      ))}
    </div>
  );
}

export default Demo;
