import React, { useRef, useState, useEffect } from "react";

import IMG from "./sdf.png";
import VID from "./t1.mp4";

function DrawCanvas(props) {
  const canvasRef = useRef(null);
  ///

  const [positions, setPositions] = useState([]);

  const handleOnClick = (event) => {
    const imageRect = event.target.getBoundingClientRect();
    const mouseX = event.clientX - imageRect.left;
    const mouseY = event.clientY - imageRect.top;
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
    canvas.width = 500;
    canvas.height = 500;
    canvas.style.width = `${500}px`;
    canvas.style.height = `${500}px`;

    const context = canvas.getContext("2d");
    context.scale(1, 1);
    context.lineCap = "round";
    context.lineWidth = 4;
    console.log(positions);
    if (positions.length >= 2) {
      for (let i = 0; i < positions.length; i++) {
        if (i > 0) {
          drawLine(context, positions[i - 1], positions[i]);
        }
      }
      drawLine(context, positions[positions.length - 1], positions[0]);
    }
  }, [positions]);

  return (
    <div>
      <canvas
        onClick={handleOnClick}
        ref={canvasRef}
        width={500}
        height={500}
        style={{
          position: "absolute",
          zIndex: 999,
        }}
      />
      {/* <video id="v" controls loop width="500">
        <source src={VID} type="video/mp4" />
      </video> */}
      <img src={IMG} width="500" />
    </div>
  );
}

export default DrawCanvas;
