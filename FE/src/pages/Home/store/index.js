import { hookstate } from "@hookstate/core";


const initValueHomeState = {
  fileNames: [],
  fileUrls: [],
  arrPositions: []
};

const homeStore = hookstate(initValueHomeState);

export default homeStore
