<template>
  <div class="flex-1 space-y-4 p-4 md:p-8 pt-6">
    <div class="flex items-center justify-between space-y-2">
      <h2 class="text-3xl font-bold tracking-tight">Users Management</h2>
    </div>

    <Card>
      <CardHeader>
        <CardTitle>All Users</CardTitle>
        <CardDescription>
          Manage system users and their roles.
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div class="flex flex-col sm:flex-row gap-4 mb-6">
          <Input v-model="filters.search" placeholder="Search name, email, username..." class="w-full sm:max-w-xs" />
          
          <select v-model="filters.role" class="flex h-10 w-full sm:w-[180px] items-center justify-between rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2">
            <option value="">All Roles</option>
            <option value="Admin">Admin</option>
            <option value="Receptionist">Receptionist</option>
            <option value="Doctor">Doctor</option>
            <option value="Patient">Patient</option>
          </select>
          
          <select v-model="filters.is_active" class="flex h-10 w-full sm:w-[180px] items-center justify-between rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2">
            <option value="">All Statuses</option>
            <option value="true">Active</option>
            <option value="false">Inactive</option>
          </select>
        </div>
        <div v-if="isLoading" class="text-gray-500 py-4">
          Loading users...
        </div>
        <div v-else-if="error" class="text-red-500 py-4">
          {{ error }}
        </div>
        <div v-else class="overflow-x-auto">
          <table class="w-full text-sm text-left text-gray-500">
            <thead class="text-xs text-gray-700 uppercase bg-gray-50">
              <tr>
                <th scope="col" class="px-6 py-3">ID</th>
                <th scope="col" class="px-6 py-3">Username</th>
                <th scope="col" class="px-6 py-3">Name</th>
                <th scope="col" class="px-6 py-3">Email</th>
                <th scope="col" class="px-6 py-3">Primary Role</th>
                <th scope="col" class="px-6 py-3">Status</th>
                <th scope="col" class="px-6 py-3">Action</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="user in users" :key="user.id" class="bg-white border-b hover:bg-gray-50">
                <td class="px-6 py-4 font-medium text-gray-900 whitespace-nowrap">
                  {{ user.id }}
                </td>
                <td class="px-6 py-4">
                  {{ user.username }}
                </td>
                <td class="px-6 py-4">
                  {{ user.first_name }} {{ user.last_name }}
                </td>
                <td class="px-6 py-4">
                  {{ user.email }}
                </td>
                <td class="px-6 py-4">
                  {{ user.primary_role }}
                </td>
                <td class="px-6 py-4">
                  <span
                    class="px-2 py-1 text-xs rounded-full font-medium"
                    :class="user.is_active ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'"
                  >
                    {{ user.is_active ? 'Active' : 'Inactive' }}
                  </span>
                </td>
                <td class="px-6 py-4">
                  <Button variant="outline" size="sm" @click="router.push(`/admin/users/${user.id}`)">
                    {{ canEdit ? 'Edit' : 'View' }}
                  </Button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <div v-if="totalPages > 1 && !isLoading" class="flex items-center justify-between mt-4 px-2 py-4 border-t">
          <div class="text-sm text-gray-500">
            Showing {{ users.length }} of {{ totalCount }} users
          </div>
          <div class="flex gap-2">
            <Button variant="outline" size="sm" :disabled="currentPage === 1" @click="fetchUsers(currentPage - 1)">
              Previous
            </Button>
            <span class="flex items-center px-2 text-sm font-medium">Page {{ currentPage }} of {{ totalPages }}</span>
            <Button variant="outline" size="sm" :disabled="currentPage >= totalPages" @click="fetchUsers(currentPage + 1)">
              Next
            </Button>
          </div>
        </div>
      </CardContent>
    </Card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, watch, computed } from "vue";
import { useRouter } from "vue-router";
import { userService } from "@/services/userService";
import { useAuth } from "@/composables/useAuth";

import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";

const router = useRouter();
const { user: currentUser } = useAuth();

const canEdit = computed(() => currentUser.value?.primary_role === 'Admin');

const users = ref([]);
const totalCount = ref(0);
const currentPage = ref(1);
const totalPages = ref(1);
const isLoading = ref(true);
const error = ref("");

const filters = reactive({
  search: "",
  role: "",
  is_active: ""
});

let debounceTimer = null;

watch(() => filters.search, () => {
  clearTimeout(debounceTimer);
  debounceTimer = setTimeout(() => {
    fetchUsers(1);
  }, 400); // 400ms debounce
});

watch([() => filters.role, () => filters.is_active], () => {
  fetchUsers(1);
});

const fetchUsers = async (page = 1) => {
  isLoading.value = true;
  error.value = "";
  try {
    const params = { page };
    if (filters.search) params.search = filters.search;
    if (filters.role) params.role = filters.role;
    if (filters.is_active !== "") params.is_active = filters.is_active;

    const data = await userService.getUsers(params);
    if (data.results) {
      users.value = data.results;
      totalCount.value = data.count;
      currentPage.value = page;
      // Defaulting to 10 items per page if PAGE_SIZE isn't in response
      totalPages.value = Math.ceil(data.count / 10) || 1;
    } else {
      users.value = data;
      totalCount.value = data.length;
      totalPages.value = 1;
    }
  } catch (err) {
    error.value = "Failed to load users.";
    console.error(err);
  } finally {
    isLoading.value = false;
  }
};

onMounted(() => {
  fetchUsers();
});
</script>
