import { useHookstate } from "@hookstate/core";
import homeStore from "../store";

const useQueryHome = () => {
  const homeState = useHookstate(homeStore);
  return {
    homeState,
  };
};

export default useQueryHome;
