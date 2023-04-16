import { Col, Row } from "antd";
import React from "react";
import styles from "./Home.module.css";
import DetailContent from "./subcomponent/DetailContent";
import MultiCamera from "./subcomponent/MultiCamera";
import EstimationDisplay from "./subcomponent/EstimationDisplay";
import { useHookstate } from "@hookstate/core";
import homeStore from "./store";
import Header from "../../conponents/Header";

function Home() {
  // eslint-disable-next-line
  const homeState = useHookstate(homeStore);

  return (
    <div className={styles.container}>
      <Header />
      <Row className={styles.content}>
        <Col span={6} className={styles.barContent}>
          <div style={{ height: "50%"}}>
            <MultiCamera />
          </div>
          <div style={{ height: "50%" }}>
            <DetailContent />
          </div>
        </Col>
        <Col span={18}>
          <EstimationDisplay />
        </Col>
      </Row>
    </div>
  );
}

export default Home;
