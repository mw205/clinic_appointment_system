<script setup>
import { computed, onMounted, watch } from "vue";
import { storeToRefs } from "pinia";
import { toast } from "vue-sonner";
import { useRouter } from "vue-router";

import AppointmentList from "@/components/appointments/AppointmentList.vue";
import QueuePaginator from "@/components/appointments/QueuePaginator.vue";
import { useAppointments } from "@/composables/useAppointments.js";
import { Button } from "@/components/ui/button/index.ts";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card/index.ts";
import { Input } from "@/components/ui/input/index.ts";
import { Label } from "@/components/ui/label/index.ts";
import { NativeSelect, NativeSelectOption } from "@/components/ui/native-select/index.ts";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs/index.ts";
import { useAppointmentsStore } from "@/stores/Appointments.js";

const props = defineProps({
  mode: {
    type: String,
    required: true,
    validator: (value) => ["doctor", "receptionist"].includes(value),
  },
  title: {
    type: String,
    default: "Today's Schedule",
  },
  canStartConsultation: {
    type: Boolean,
    default: false,
  },
  canViewRecord: {
    type: Boolean,
    default: false,
  },
});

const store = useAppointmentsStore();
const router = useRouter();
const { appointments, pagination } = storeToRefs(store);
const isPaginated = computed(() => props.mode === "receptionist");
const showDoctorFilter = computed(() => props.mode === "receptionist");
const {
  filters,
  stats,
  appointmentsByTab,
  hasActiveFilters,
  requestParams,
  resetFilters,
  calculateWaitTime,
} = useAppointments(appointments, {
  includeDoctorNameFilter: showDoctorFilter.value,
});

let filtersDebounceId = null;

const formattedDate = new Intl.DateTimeFormat("en-US", {
  weekday: "long",
  year: "numeric",
  month: "long",
  day: "numeric",
}).format(new Date());

const loadAppointments = async (params = {}) => {
  if (props.mode === "doctor") {
    await store.loadDoctorDailyQueue(params);
    return;
  }

  await store.loadAppointments(params);
};

const reloadCurrentQueue = async () => {
  const params = isPaginated.value
    ? { ...requestParams.value, page: pagination.value.currentPage }
    : requestParams.value

  await loadAppointments(params);
};

async function handleCheckIn(id) {
  try {
    const res = await store.checkInAppointment(id);
    await reloadCurrentQueue();
    toast.success(res.message || "Checked in successfully");
  } catch (err) {
    toast.error(err.response?.data?.message || "Something went wrong");
  }
}

const handleComplete = (id) => {
  if (!props.canStartConsultation) {
    return;
  }

  router.push(`/doctor/appointments/${id}/consultation`);
};

const handleViewRecord = () => {
  if (!props.canViewRecord) {
    return;
  }
};

const handleNoShow = async (id) => {
  try {
    const res = await store.hideAppointment(id);
    await reloadCurrentQueue();
    toast.success(res.message || "Hidden in successfully");
  } catch (err) {
    toast.error(err.response?.data?.message || "Something went wrong");
  }
};

const handlePageChange = async (page) => {
  await loadAppointments({ ...requestParams.value, page });
};

watch(
  filters,
  () => {
    clearTimeout(filtersDebounceId);
    filtersDebounceId = setTimeout(() => {
      const params = isPaginated.value
        ? { ...requestParams.value, page: 1 }
        : requestParams.value

      loadAppointments(params);
    }, 300);
  },
  { deep: true },
);

onMounted(async () => {
  await loadAppointments();
});
</script>

<template>
  <div class="space-y-6">
    <Card>
      <CardHeader>
        <div class="flex items-center justify-between">
          <div>
            <CardTitle>{{ title }}</CardTitle>
            <CardDescription>{{ formattedDate }}</CardDescription>
          </div>
        </div>
      </CardHeader>

      <CardContent>
        <div class="mb-6 grid gap-4 md:grid-cols-2 xl:grid-cols-4">
          <div class="space-y-2">
            <Label for="patient-name-filter">Patient Name</Label>
            <Input
              id="patient-name-filter"
              v-model="filters.patientName"
              placeholder="Search by patient name"
            />
          </div>

          <div v-if="showDoctorFilter" class="space-y-2">
            <Label for="doctor-name-filter">Doctor Name</Label>
            <Input
              id="doctor-name-filter"
              v-model="filters.doctorName"
              placeholder="Search by doctor name"
            />
          </div>

          <div class="space-y-2">
            <Label for="status-filter">Status</Label>
            <NativeSelect id="status-filter" v-model="filters.status" class="w-full">
              <NativeSelectOption value="all">All statuses</NativeSelectOption>
              <NativeSelectOption value="confirmed">Confirmed</NativeSelectOption>
              <NativeSelectOption value="checked_in">Checked In</NativeSelectOption>
              <NativeSelectOption value="completed">Completed</NativeSelectOption>
              <NativeSelectOption value="no_show">No Show</NativeSelectOption>
            </NativeSelect>
          </div>

          <div class="space-y-2">
            <Label for="start-date-filter">Start Date</Label>
            <Input
              id="start-date-filter"
              v-model="filters.startDate"
              type="date"
            />
          </div>

          <div class="space-y-2">
            <Label for="end-date-filter">End Date</Label>
            <Input
              id="end-date-filter"
              v-model="filters.endDate"
              type="date"
            />
          </div>
        </div>

        <div class="mb-6 flex items-center justify-between gap-3">
          <p class="text-sm text-gray-500">
            Showing {{ stats.total }} appointments
          </p>
          <Button
            v-if="hasActiveFilters"
            variant="outline"
            size="sm"
            @click="resetFilters"
          >
            Clear Filters
          </Button>
        </div>

        <Tabs default-value="all" class="space-y-4">
          <TabsList>
            <TabsTrigger value="all">All ({{ stats.total }})</TabsTrigger>
            <TabsTrigger value="checked_in">Checked In ({{ stats.checkedIn }})</TabsTrigger>
            <TabsTrigger value="no_show">Hidden ({{ stats.hidden }})</TabsTrigger>
          </TabsList>

          <TabsContent value="all">
            <AppointmentList
              :appointments="appointmentsByTab.all"
              :calculate-wait-time="calculateWaitTime"
              :can-start-consultation="canStartConsultation"
              :can-view-record="canViewRecord"
              @check-in="handleCheckIn"
              @no-show="handleNoShow"
              @complete="handleComplete"
              @view-record="handleViewRecord"
              empty-message="No appointments match the current filters."
            />
          </TabsContent>

          <TabsContent value="checked_in">
            <AppointmentList
              :appointments="appointmentsByTab.checked_in"
              :calculate-wait-time="calculateWaitTime"
              :can-start-consultation="canStartConsultation"
              :can-view-record="canViewRecord"
              @check-in="handleCheckIn"
              @no-show="handleNoShow"
              @complete="handleComplete"
              @view-record="handleViewRecord"
              empty-message="No checked-in appointments match the current filters."
            />
          </TabsContent>

          <TabsContent value="no_show">
            <AppointmentList
              :appointments="appointmentsByTab.no_show"
              :calculate-wait-time="calculateWaitTime"
              :can-start-consultation="canStartConsultation"
              :can-view-record="canViewRecord"
              @check-in="handleCheckIn"
              @no-show="handleNoShow"
              @complete="handleComplete"
              @view-record="handleViewRecord"
              empty-message="No hidden appointments match the current filters."
            />
          </TabsContent>
        </Tabs>

        <QueuePaginator
          v-if="isPaginated"
          :current-page="pagination.currentPage"
          :total-pages="pagination.totalPages"
          :total-items="pagination.count"
          @change="handlePageChange"
        />
      </CardContent>
    </Card>
  </div>
</template>
