<script setup>
import { computed, onBeforeUnmount, onMounted, watch } from "vue";
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
  canConfirm: {
    type: Boolean,
    default: false,
  },
  fetchMode: {
    type: String,
    default: "auto",
    validator: (value) => ["auto", "list", "doctor-queue"].includes(value),
  },
  fixedParams: {
    type: Object,
    default: () => ({}),
  },
  showTabs: {
    type: Boolean,
    default: true,
  },
  showStatusFilter: {
    type: Boolean,
    default: true,
  },
  useTimeRangeFilters: {
    type: Boolean,
    default: false,
  },
});

const store = useAppointmentsStore();
const router = useRouter();
const { appointments, pagination } = storeToRefs(store);
const isPaginated = computed(() => {
  if (props.fetchMode === "list") {
    return true;
  }

  if (props.fetchMode === "doctor-queue") {
    return false;
  }

  return props.mode === "receptionist";
});
const showDoctorFilter = computed(() => props.mode === "receptionist");
const rangeFilterBaseDate = computed(() => props.fixedParams.date || new Date().toISOString().slice(0, 10));
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
  useTimeRangeFilters: props.useTimeRangeFilters,
  baseDate: rangeFilterBaseDate.value,
});

let filtersDebounceId = null;

const formattedDate = new Intl.DateTimeFormat("en-US", {
  weekday: "long",
  year: "numeric",
  month: "long",
  day: "numeric",
}).format(new Date());

const effectiveRequestParams = computed(() => {
  const params = {
    ...requestParams.value,
    ...props.fixedParams,
  };

  if (!props.showStatusFilter && props.fixedParams.status) {
    delete params.status;
    params.status = props.fixedParams.status;
  }

  return params;
});

const hasVisibleFilters = computed(() => {
  if (!hasActiveFilters.value) {
    return false;
  }

  return (
    filters.value.patientName.trim() !== ""
    || (showDoctorFilter.value && filters.value.doctorName.trim() !== "")
    || filters.value.startDate !== ""
    || filters.value.endDate !== ""
    || (props.showStatusFilter && filters.value.status !== "all")
  );
});

const loadAppointments = async (params = {}) => {
  const finalParams = {
    ...params,
    ...props.fixedParams,
  };

  if (props.fetchMode === "list") {
    await store.loadAppointments(finalParams);
    return;
  }

  if (props.fetchMode === "doctor-queue") {
    await store.loadDoctorDailyQueue(finalParams);
    return;
  }

  if (props.mode === "doctor") {
    await store.loadDoctorDailyQueue(finalParams);
    return;
  }

  await store.loadAppointments(finalParams);
};

const reloadCurrentQueue = async () => {
  const params = isPaginated.value
    ? { ...effectiveRequestParams.value, page: pagination.value.currentPage }
    : effectiveRequestParams.value;

  await loadAppointments(params);
};

async function handleConfirm(id) {
  try {
    const res = await store.confirmAppointment(id);
    await reloadCurrentQueue();
    toast.success(res.message || "Appointment confirmed");
  } catch (err) {
    toast.error(err.response?.data?.message || err.response?.data?.error || "Something went wrong");
  }
}

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
  await loadAppointments({ ...effectiveRequestParams.value, page });
};

watch(
  filters,
  () => {
    clearTimeout(filtersDebounceId);
    filtersDebounceId = setTimeout(() => {
      const params = isPaginated.value
        ? { ...effectiveRequestParams.value, page: 1 }
        : effectiveRequestParams.value;

      loadAppointments(params);
    }, 300);
  },
  { deep: true },
);

watch(
  () => props.fixedParams,
  async () => {
    const params = isPaginated.value
      ? { ...effectiveRequestParams.value, page: 1 }
      : effectiveRequestParams.value;

    await loadAppointments(params);
  },
  { deep: true },
);

onMounted(async () => {
  await loadAppointments(effectiveRequestParams.value);
});

onBeforeUnmount(() => {
  clearTimeout(filtersDebounceId);
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

          <div v-if="showStatusFilter" class="space-y-2">
            <Label for="status-filter">Status</Label>
            <NativeSelect id="status-filter" v-model="filters.status" class="w-full">
              <NativeSelectOption value="all">All statuses</NativeSelectOption>
              <NativeSelectOption value="requested">Requested</NativeSelectOption>
              <NativeSelectOption value="confirmed">Confirmed</NativeSelectOption>
              <NativeSelectOption value="checked_in">Checked In</NativeSelectOption>
              <NativeSelectOption value="completed">Completed</NativeSelectOption>
              <NativeSelectOption value="no_show">No Show</NativeSelectOption>
            </NativeSelect>
          </div>

          <div class="space-y-2">
            <Label for="start-date-filter">{{ useTimeRangeFilters ? "Start Time" : "Start Date" }}</Label>
            <Input
              id="start-date-filter"
              v-model="filters.startDate"
              :type="useTimeRangeFilters ? 'time' : 'date'"
            />
          </div>

          <div class="space-y-2">
            <Label for="end-date-filter">{{ useTimeRangeFilters ? "End Time" : "End Date" }}</Label>
            <Input
              id="end-date-filter"
              v-model="filters.endDate"
              :type="useTimeRangeFilters ? 'time' : 'date'"
            />
          </div>
        </div>

        <div class="mb-6 flex items-center justify-between gap-3">

          <Button
            v-if="hasVisibleFilters"
            variant="outline"
            size="sm"
            @click="resetFilters"
          >
            Clear Filters
          </Button>
        </div>

        <Tabs v-if="showTabs" default-value="all" class="space-y-4">
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
              :can-confirm="canConfirm"
              @confirm="handleConfirm"
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
              :can-confirm="canConfirm"
              @confirm="handleConfirm"
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
              :can-confirm="canConfirm"
              @confirm="handleConfirm"
              @check-in="handleCheckIn"
              @no-show="handleNoShow"
              @complete="handleComplete"
              @view-record="handleViewRecord"
              empty-message="No hidden appointments match the current filters."
            />
          </TabsContent>
        </Tabs>

        <AppointmentList
          v-else
          :appointments="appointmentsByTab.all"
          :calculate-wait-time="calculateWaitTime"
          :can-start-consultation="canStartConsultation"
          :can-view-record="canViewRecord"
          :can-confirm="canConfirm"
          @confirm="handleConfirm"
          @check-in="handleCheckIn"
          @no-show="handleNoShow"
          @complete="handleComplete"
          @view-record="handleViewRecord"
          empty-message="No appointments match the current filters."
        />

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
