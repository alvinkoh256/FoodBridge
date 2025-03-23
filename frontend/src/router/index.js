import { createRouter, createWebHistory } from "vue-router";

const router = createRouter({
    history: createWebHistory(),
    routes: [
        { path: "/", component: () => import("../views/Login.vue")},
        { path: "/register", component: () => import("../views/Register.vue")}
    ],
});

export default router;