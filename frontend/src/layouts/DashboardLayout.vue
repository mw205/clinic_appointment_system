<script setup>
import Avatar from "@/components/ui/avatar/Avatar.vue";
import AvatarFallback from "@/components/ui/avatar/AvatarFallback.vue";
import Button from "@/components/ui/button/Button.vue";
import DropdownMenu from "@/components/ui/dropdown-menu/DropdownMenu.vue";
import DropdownMenuContent from "@/components/ui/dropdown-menu/DropdownMenuContent.vue";
import DropdownMenuItem from "@/components/ui/dropdown-menu/DropdownMenuItem.vue";
import DropdownMenuLabel from "@/components/ui/dropdown-menu/DropdownMenuLabel.vue";
import DropdownMenuSeparator from "@/components/ui/dropdown-menu/DropdownMenuSeparator.vue";
import DropdownMenuTrigger from "@/components/ui/dropdown-menu/DropdownMenuTrigger.vue";
import { useAuth } from "@/composables/useAuth";
import {
  Activity,
  BarChart3,
  Bell,
  Calendar,
  ClipboardList,
  Clock,
  FileText,
  LayoutDashboard,
  LogOut,
  Menu,
  Settings,
  Users,
  X
} from "lucide-vue-next";
import { computed, ref } from 'vue';
import { useRoute, useRouter } from 'vue-router';
const NAV_ITEMS = [
  {
    label: "Dashboard",
    icon: LayoutDashboard,
    path: "dashboard",
    roles: ["Patient", "Admin"],
  },
  {
    label: "Appointments",
    icon: Calendar,
    path: "appointments",
    roles: ["Patient", "Doctor", "Receptionist"],
  },
  {
    label: "Book Appointment",
    icon: Calendar,
    path: "book",
    roles: ["Patient"],
  },
  {
    label: "History",
    icon: FileText,
    path: "history",
    roles: ["Patient"],
  },
  {
    label: "Medical Records",
    icon: FileText,
    path: "records",
    roles: ["Doctor"],
  },
  {
    label: "Queue Management",
    icon: Clock,
    path: "queue",
    roles: ["Receptionist", "Doctor"],
  },
  {
    label: "Doctor Schedules",
    icon: ClipboardList,
    path: "schedules",
    roles: ["Receptionist", "Admin", "Doctor"],
  },
  { label: "Analytics", icon: BarChart3, path: "analytics", roles: ["Admin"] },
  { label: "User Management", icon: Users, path: "users", roles: ["Admin", "Receptionist"], fullPath: "/admin/users" },
  { label: "Settings", icon: Settings, path: "settings", roles: ["Patient", "Doctor", "Receptionist", "Admin"], fullPath: "/settings" },
];
const router = useRouter();
const route = useRoute();
const { user, logout } = useAuth();
const sidebarOpen = ref(false);
const userInitials = computed(() => {
  if (!user.value) return ''

  const names = [user.value.first_name, user.value.last_name]
    .filter(Boolean)
    .map((name) => name.trim()[0])
    .filter(Boolean)

  if (names.length) {
    return names.join('').slice(0, 2).toUpperCase()
  }

  return user.value.username?.slice(0, 2).toUpperCase() || 'U'
});

const handleLogout = () => {
  logout();
}

const visibleNavItems = computed(() => {
  if (!user.value) return [];
  return NAV_ITEMS.filter((item) => item.roles.includes(user.value.primary_role));
});
const routeNameFormatted = computed(() => {
  if (route.name && typeof route.name === "string") {
    return route.name.replace(/-/g, " ");
  }
  return "Dashboard";
});
const isActivePath = (item) => {
  if (item.fullPath) {
    return route.path.startsWith(item.fullPath);
  }
  return route.path.includes(item.path) || route.name?.toString().includes(item.path);
};

const handleNavigate = (pathOrItem) => {
  sidebarOpen.value = false;
  if (!user.value) return;

  if (typeof pathOrItem === 'object' && pathOrItem !== null) {
    if (pathOrItem.fullPath) {
      router.push(pathOrItem.fullPath);
    } else {
      const role = user.value.primary_role.toLowerCase();
      router.push(`/${role}/${pathOrItem.path}`);
    }
    return;
  }

  // Handle string paths (like from dropdown)
  if (pathOrItem === "profile" || pathOrItem === "settings") {
    router.push("/settings");
  } else {
    const role = user.value.primary_role.toLowerCase();
    router.push(`/${role}/${pathOrItem}`);
  }
};

</script>

<template>
  <div v-if="user" class="min-h-screen bg-gray-50">
    <aside :class="[
      'fixed inset-y-0 left-0 z-50 w-64 bg-white border-r border-gray-200 transform transition-transform duration-200 ease-in-out lg:translate-x-0',
      sidebarOpen ? 'translate-x-0' : '-translate-x-full'
    ]">
      <div class="flex flex-col h-full">
        <!--logo-->
        <div class="h-16 flex items-center gap-3 px-6 border-b border-gray-200">
          <div class="p-2 bg-blue-600 rounded-lg">
            <Activity class="w-6 h-6 text-white" />
          </div>
          <div>
            <h1 class="font-semibold text-gray-900">HealthCare</h1>
            <p class="text-xs text-gray-500">Clinic System</p>
          </div>
        </div>
        <!--navigation items-->
        <nav class="flex-1 overflow-y-auto px-3 py-4">
          <div class="space-y-1">
            <button v-for="item in visibleNavItems" :key="item.label" @click="handleNavigate(item)" :class="[
              'w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors',
              isActivePath(item)
                ? 'bg-blue-50 text-blue-700'
                : 'text-gray-700 hover:bg-gray-100'
            ]">
              <component :is="item.icon" class="w-5 h-5" />
              {{ item.label }}
            </button>
          </div>
        </nav>
        <!--profile-->
        <div class="p-4 border-t border-gray-200">
          <div class="flex items-center gap-3 px-3 py-2 rounded-lg bg-gray-50">
            <Avatar class="h-9 w-9">
              <AvatarFallback
                class="flex h-full w-full items-center justify-center bg-blue-600 text-xs font-semibold uppercase leading-none text-white">
                {{ userInitials }}
              </AvatarFallback>
            </Avatar>
            <div class="flex-1 min-w-0">
              <p class="text-sm font-medium text-gray-900 truncate">
                {{ user.first_name }} {{ user.last_name }}
              </p>
              <p class="text-xs text-gray-500 capitalize">{{ user.primary_role }}</p>
            </div>
          </div>
        </div>
      </div>
    </aside>
    <div class="lg:pl-64">
      <header class="sticky top-0 z-40 h-16 bg-white border-b border-gray-200">
        <div class="h-full px-4 flex items-center justify-between">
          <div class="flex items-center gap-3">
            <Button variant="ghost" size="icon" class="lg:hidden" @click="sidebarOpen = !sidebarOpen">
              <X v-if="sidebarOpen" class="h-5 w-5" />
              <Menu v-else class="h-5 w-5" />
            </Button>
            <div>
              <h2 class="text-lg font-semibold text-gray-900 capitalize">
                {{ routeNameFormatted }}
              </h2>
            </div>
          </div>

          <div class="flex items-center gap-2">
            <Button variant="ghost" size="icon" class="relative">
              <Bell class="h-5 w-5" />
              <span class="absolute top-1 right-1 h-2 w-2 bg-red-500 rounded-full" />
            </Button>

            <DropdownMenu>
              <DropdownMenuTrigger as-child>
                <Button variant="ghost" class="gap-2">
                  <Avatar class="h-8 w-8">
                    <AvatarFallback
                      class="flex h-full w-full items-center justify-center bg-blue-600 text-xs font-semibold uppercase leading-none text-white">
                      {{ userInitials }}
                    </AvatarFallback>
                  </Avatar>
                  <span class="hidden md:inline text-sm">
                    {{ user.first_name }} {{ user.last_name }}
                  </span>
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end" class="w-56">
                <DropdownMenuLabel>
                  <div>
                    <p class="font-medium">{{ user.first_name }} {{ user.last_name }}</p>
                    <p class="text-xs font-normal text-gray-500">{{ user.email }}</p>
                  </div>
                </DropdownMenuLabel>
                <DropdownMenuSeparator />
                <DropdownMenuItem @click="handleNavigate('settings')">
                  <Settings class="mr-2 h-4 w-4" />
                  Settings
                </DropdownMenuItem>
                <DropdownMenuSeparator />
                <DropdownMenuItem @click="handleLogout" class="text-red-600">
                  <LogOut class="mr-2 h-4 w-4" />
                  Logout
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          </div>
        </div>
      </header>

      <!-- Page Content -->
      <main class="p-4 md:p-6 lg:p-8">
        <router-view />
      </main>
    </div>

    <!-- Mobile Sidebar Overlay -->
    <div v-if="sidebarOpen" class="fixed inset-0 bg-black/50 z-40 lg:hidden" @click="sidebarOpen = false" />
  </div>
</template>
