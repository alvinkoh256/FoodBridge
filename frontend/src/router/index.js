import { createRouter, createWebHistory } from "vue-router";
import store from "../store"

const router = createRouter({
    history: createWebHistory(),
    routes: [
        { path: "/", component: () => import("../views/Login.vue")},
        { path: "/register", component: () => import("../views/Register.vue")},
        { path: "/home", component: () => import("../views/VolunteerHome.vue"), meta: { requiresAuth: true, role: 'volunteer' } }
    ],
});

//Route Protection
router.beforeEach((to, from, next) => {
    const isAuthenticated = store.getters.isAuthenticated;
    const userRole = store.getters.userRole;

    if (to.meta.requiresAuth && !isAuthenticated) {
        next('/'); // Redirect to login if not authenticated
    } else if (to.meta.role && to.meta.role !== userRole) {
        next('/unauthorized'); // Redirect to Unauthorized page if role doesn't match
    } else {
        next(); // Allow navigation
    }
});


export default router;