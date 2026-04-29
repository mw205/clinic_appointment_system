<script setup>
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { Table, TableBody, TableCell, TableEmpty, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { getAppointments, normalizeApiError } from "@/services/appointmentService";
import { CalendarCheck, CalendarClock, ClipboardList, Stethoscope } from "lucide-vue-next";
import { computed, onMounted, ref } from "vue";
import { RouterLink } from "vue-router";

const appointments = ref([]);
const loading = ref(true);
const errorMessage = ref("");

const upcomingAppointments = computed(() =>
  appointments.value.filter((appointment) =>
    ["requested", "confirmed", "checked_in"].includes(appointment.status)
    && new Date(appointment.start_time) >= new Date()
  )
);

const completedAppointments = computed(() =>
  appointments.value.filter((appointment) => appointment.status === "completed")
);

const nextAppointment = computed(() => {
  return [...upcomingAppointments.value].sort(
    (a, b) => new Date(a.start_time) - new Date(b.start_time)
  )[0];
});

const stats = computed(() => [
  {
    label: "Appointments",
    value: appointments.value.length,
    icon: ClipboardList,
  },
  {
    label: "Upcoming",
    value: upcomingAppointments.value.length,
    icon: CalendarClock,
  },
  {
    label: "Completed",
    value: completedAppointments.value.length,
    icon: CalendarCheck,
  },
]);

function formatDateTime(value) {
  return new Intl.DateTimeFormat(undefined, {
    dateStyle: "medium",
    timeStyle: "short",
  }).format(new Date(value));
}

function statusVariant(status) {
  const variants = {
    confirmed: "default",
    completed: "secondary",
    cancelled: "destructive",
    no_show: "destructive",
    requested: "outline",
    checked_in: "secondary",
  };

  return variants[status] ?? "outline";
}

async function loadAppointments() {
  loading.value = true;
  errorMessage.value = "";

  try {
    const data = await getAppointments({
      ordering: "start_time",
      page_size: 50,
    });

    appointments.value = data.results ?? data;
  } catch (error) {
    errorMessage.value = normalizeApiError(error, "Unable to load appointments.");
  } finally {
    loading.value = false;
  }
}

onMounted(loadAppointments);
</script>

<template>
  <div class="space-y-6">
    <div class="flex flex-col gap-1">
      <h1 class="text-2xl font-semibold text-gray-900">Patient Dashboard</h1>
      <p class="text-sm text-gray-500">Track your appointments and consultation history.</p>
    </div>

    <div v-if="loading" class="grid gap-4 md:grid-cols-3">
      <Skeleton v-for="item in 3" :key="item" class="h-28 rounded-lg" />
    </div>

    <div v-else class="grid gap-4 md:grid-cols-3">
      <Card v-for="item in stats" :key="item.label">
        <CardHeader class="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle class="text-sm font-medium text-gray-600">{{ item.label }}</CardTitle>
          <component :is="item.icon" class="h-5 w-5 text-blue-600" />
        </CardHeader>
        <CardContent>
          <div class="text-3xl font-semibold text-gray-900">{{ item.value }}</div>
        </CardContent>
      </Card>
    </div>

    <Card v-if="!loading && nextAppointment">
      <CardHeader>
        <CardTitle class="flex items-center gap-2 text-lg">
          <Stethoscope class="h-5 w-5 text-blue-600" />
          Next Appointment
        </CardTitle>
      </CardHeader>
      <CardContent class="grid gap-2 text-sm text-gray-700 md:grid-cols-3">
        <div>
          <p class="text-xs font-medium uppercase text-gray-500">Doctor</p>
          <p class="font-medium text-gray-900">{{ nextAppointment.doctor.name }}</p>
        </div>
        <div>
          <p class="text-xs font-medium uppercase text-gray-500">Time</p>
          <p class="font-medium text-gray-900">{{ formatDateTime(nextAppointment.start_time) }}</p>
        </div>
        <div>
          <p class="text-xs font-medium uppercase text-gray-500">Status</p>
          <Badge :variant="statusVariant(nextAppointment.status)">
            {{ nextAppointment.status }}
          </Badge>
        </div>
      </CardContent>
    </Card>

    <Card>
      <CardHeader>
        <CardTitle>My Appointments</CardTitle>
      </CardHeader>
      <CardContent>
        <div v-if="errorMessage" class="rounded-lg border border-red-200 bg-red-50 p-4 text-sm text-red-700">
          {{ errorMessage }}
        </div>

        <Table v-else>
          <TableHeader>
            <TableRow>
              <TableHead>Doctor</TableHead>
              <TableHead>Date</TableHead>
              <TableHead>Status</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            <TableRow v-for="appointment in appointments" :key="appointment.id">
              <TableCell>
                <RouterLink
                  :to="`/patient/appointments/${appointment.id}`"
                  class="font-medium text-blue-700 hover:underline"
                >
                  {{ appointment.doctor.name }}
                </RouterLink>
              </TableCell>
              <TableCell>{{ formatDateTime(appointment.start_time) }}</TableCell>
              <TableCell>
                <Badge :variant="statusVariant(appointment.status)">
                  {{ appointment.status }}
                </Badge>
              </TableCell>
            </TableRow>
            <TableEmpty v-if="!appointments.length">
              No appointments found.
            </TableEmpty>
          </TableBody>
        </Table>
      </CardContent>
    </Card>
  </div>
</template>
