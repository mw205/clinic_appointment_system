<template>
  <div class="flex-1 space-y-4 p-4 md:p-8 pt-6">
    <div class="flex items-center justify-between space-y-2">
      <h2 class="text-3xl font-bold tracking-tight">Settings</h2>
    </div>
    
    <div class="flex flex-col space-y-8 lg:flex-row lg:space-x-12 lg:space-y-0 mt-6">
      <aside class="-mx-4 lg:w-1/5">
        <nav class="flex space-x-2 lg:flex-col lg:space-x-0 lg:space-y-1">
          <router-link
            to="/settings/account"
            class="justify-start inline-flex items-center rounded-md px-3 py-2 text-sm font-medium hover:bg-gray-100"
            :class="{ 'bg-gray-100 text-teal-700': route.path === '/settings/account' }"
          >
            Account
          </router-link>
          
          <router-link
            v-if="['Patient', 'Doctor'].includes(user?.primary_role)"
            to="/settings/profile"
            class="justify-start inline-flex items-center rounded-md px-3 py-2 text-sm font-medium hover:bg-gray-100"
            :class="{ 'bg-gray-100 text-teal-700': route.path === '/settings/profile' }"
          >
            Profile
          </router-link>
        </nav>
      </aside>
      
      <div class="flex-1 lg:max-w-2xl">
        <router-view />
      </div>
    </div>
  </div>
</template>

<script setup>
import { useAuth } from "@/composables/useAuth";
import { useRoute } from "vue-router";

const { user } = useAuth();
const route = useRoute();
</script>
