import { Row, Dropdown } from "antd";
import React from "react";
import { LogoutOutlined } from "@ant-design/icons";
import styles from "./Header.module.css";

const items = [
  {
    key: "1",
    label: (
      <a
        target="_blank"
        rel="noopener noreferrer"
        href="https://www.facebook.com/"
      >
        Detail Account
      </a>
    ),
  },
  {
    key: "2",
    label: (
      <a
        target="_blank"
        rel="noopener noreferrer"
        href="https://www.aliyun.com"
      >
        <div>
          <span>
            <LogoutOutlined style={{ paddingRight: 4 }} />
          </span>
          <span>Logout</span>
        </div>
      </a>
    ),
  },
];

const Header = () => {
  return (
    <Row justify={"space-between"} align={"middle"} className={styles.content}>
      <div className={styles.logoText}>System Name</div>
      <Dropdown
        menu={{
          items,
        }}
        placement="bottomLeft"
      >
        <Row>
          <div>Warrior</div>
        </Row>
      </Dropdown>
    </Row>
  );
};

export default Header;
