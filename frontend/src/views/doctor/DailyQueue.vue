<script setup>
import {useDoctorAppointmentsStore} from "@/stores/DoctorAppointments.js";
import {onMounted, watch} from "vue";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle
} from "@/components/ui/card/index.ts";
import {Tabs, TabsContent, TabsList, TabsTrigger} from "@/components/ui/tabs/index.ts";
import {Button} from "@/components/ui/button/index.ts";
import {Input} from "@/components/ui/input/index.ts";
import {Label} from "@/components/ui/label/index.ts";
import {NativeSelect, NativeSelectOption} from "@/components/ui/native-select/index.ts";
import {storeToRefs} from "pinia";
import {toast} from "vue-sonner";
import router from "@/router/index.js";
import AppointmentList from "@/components/appointments/AppointmentList.vue";
import { useAppointments } from "@/composables/useAppointments.js";
import * as doctorAppointmentsService from "@/services/doctorAppointments.js";

const store = useDoctorAppointmentsStore();
const { dailyQueue } = storeToRefs(store);
const { filters, stats, appointmentsByTab, hasActiveFilters, requestParams, resetFilters, calculateWaitTime } = useAppointments(dailyQueue);
let filtersDebounceId = null;

onMounted(() => {
    store.loadDailyQueue()
})

const today = new Date()

const formattedDate = new Intl.DateTimeFormat('en-US', {
  weekday: 'long',
  year: 'numeric',
  month: 'long',
  day: 'numeric',
}).format(today)

async function handleCheckIn(id) {
  try {
    const res = await store.checkInAppointment(id)
    toast.success(res.message || 'Checked in successfully')
  } catch (err) {
    console.error(err)
    toast.error(err.response?.data?.message || 'Something went wrong')
  }
}

const handleComplete = () => {
  handleNavigate('emr-form');
};

const handleViewRecord = () => {
  handleNavigate('records');
};

const handleNavigate = (path) => {
  router.push(`/doctor/${path}`);
};

const handleNoShow = async (id) => {
  try {
    const res = await store.hideAppointment(id)
    toast.success(res.message || 'Hidden in successfully')
  } catch (err) {
    console.error(err)
    toast.error(err.response?.data?.message || 'Something went wrong')
  }
}


watch(
  filters,
  () => {
    clearTimeout(filtersDebounceId);
    filtersDebounceId = setTimeout(() => {
      store.loadDailyQueue(requestParams.value);
    }, 300);
  },
  { deep: true },
);


</script>

<template>
<div class="space-y-6">
  <Card>
      <CardHeader>
        <div class="flex items-center justify-between">
          <div>
            <CardTitle>Today's Schedule</CardTitle>
            <CardDescription>{{formattedDate}}</CardDescription>
          </div>
<!--          <Button variant="outline" @click="handleNavigate('schedules')">-->
<!--            View Calendar-->
<!--          </Button>-->
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
            <TabsTrigger value="checked_in">Checked In ({{stats.checkedIn}})</TabsTrigger>
            <TabsTrigger value="no_show">Hidden ({{ stats.hidden }})</TabsTrigger>
          </TabsList>

          <TabsContent value="all">
            <AppointmentList
              :appointments="appointmentsByTab.all"
              :calculate-wait-time="calculateWaitTime"
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
              @check-in="handleCheckIn"
              @no-show="handleNoShow"
              @complete="handleComplete"
              @view-record="handleViewRecord"
              empty-message="No hidden appointments match the current filters."
            />
          </TabsContent>

        </Tabs>
      </CardContent>
    </Card>
</div>
</template>

<style scoped>

</style>
