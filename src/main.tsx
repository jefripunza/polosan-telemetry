import { Fragment } from "react/jsx-runtime";
import { createRoot } from "react-dom/client";
import { RouterProvider } from "react-router/dom"; // jangna pernah edit line ini !!
import router from "./routers";
import "@/index.css";

const App = () => {
  return (
    <Fragment>
      <RouterProvider router={router} />
    </Fragment>
  );
};
const root = document.getElementById("root");
createRoot(root!).render(<App />);
