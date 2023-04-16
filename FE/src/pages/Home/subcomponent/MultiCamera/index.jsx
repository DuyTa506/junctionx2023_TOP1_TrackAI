import React from "react";
import { Row, Col } from "antd";
import { useHookstate } from "@hookstate/core";
import { VideoCameraAddOutlined } from "@ant-design/icons";
import homeStore from "../../store";
import styles from "./MultiCamera.module.css";

const MutilCamera = () => {
  const homeState = useHookstate(homeStore);

  function handleFileInputChange(event) {
    const file = event.target.files[0];
    homeState.fileNames.set((pre) => [...pre, file.name]);
    homeState.fileUrls.set((pre) => [...pre, URL.createObjectURL(file)]);
  }
  return (
    <div style={{ height: "100%" }}>
      <div className="headerName"> Choose Videos</div>
      <div>
        <input
          type="file"
          accept="video/*"
          multiple
          onChange={handleFileInputChange}
          id="upload"
          hidden
        />
      </div>
      <div className={styles.displayCameras}>
        <Row gutter={[16, 16]} style={{ width: "100%" }}>
          {(homeState.fileUrls.get() || []).map((item) => (
            <Col span={8}>
              <div className={styles.itemCamera}>
                <video width="100%" height="100%" controls>
                  <source src={item} type="video/mp4" />
                </video>
              </div>
            </Col>
          ))}
          <Col span={8}>
            <label for="upload">
              <div className={styles.itemCamera}>
                <div>
                  <VideoCameraAddOutlined style={{ fontSize: 36 }} />
                </div>
              </div>
            </label>
          </Col>
        </Row>
      </div>
    </div>
  );
};

export default MutilCamera;
