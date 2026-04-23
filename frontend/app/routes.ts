import { type RouteConfig, index, route, layout } from "@react-router/dev/routes";

export default [
  index("routes/_index.tsx"),
  route("login", "routes/login.tsx"),
  route("chat", "routes/chat.tsx"),
  layout("routes/admin.tsx", [
    route("admin/users", "routes/admin.users.tsx"),
    route("admin/documents", "routes/admin.documents.tsx"),
  ]),
] satisfies RouteConfig;
