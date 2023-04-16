import { Space } from "antd";
import React from "react";

const DetailContent = () => {
  return (
    <div>
      <div className="headerName">Details Estimation</div>
      <Space direction="vertical" align="start">
        <Space>
          <span style={{ fontSize: 18, fontWeight: 600 }}>Overlapping area:</span>
          <span>400m2</span>
        </Space>
        <Space>
          <span style={{ fontSize: 18, fontWeight: 600 }} >Cameras Need:</span>
          <span>4</span>
        </Space>
      </Space>
    </div>
  );
};

export default DetailContent;
