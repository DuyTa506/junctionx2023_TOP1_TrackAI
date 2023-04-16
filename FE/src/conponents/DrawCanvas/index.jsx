import React, { useRef, useEffect } from "react";

function DrawCanvas(props) {
  const canvasRef = useRef(null);
  ///

  const handleOnClick = (event) => {
    const imageRect = event.target.getBoundingClientRect();
    const mouseX = event.clientX - imageRect.left;
    const mouseY = event.clientY - imageRect.top;
    const newPositions = [...props.positions, { x: mouseX, y: mouseY }];
    props.setPositions(newPositions);
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
    const _postitons = props.positions;
    if (_postitons.length >= 2) {
      for (let i = 0; i < _postitons.length; i++) {
        if (i > 0) {
          drawLine(context, _postitons[i - 1], _postitons[i]);
        }
      }
      drawLine(context, _postitons[_postitons.length - 1], _postitons[0]);
    }
  }, [props.positions]);
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
      <img src={props.src} width="500" alt="Loi hien thi" />
    </div>
  );
}

export default DrawCanvas;
