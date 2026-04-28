<script setup>
import {useDoctorAppointmentsStore} from "@/stores/DoctorAppointments.js";
import {onMounted} from "vue";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle
} from "@/components/ui/card/index.ts";
import {Tabs, TabsContent, TabsList, TabsTrigger} from "@/components/ui/tabs/index.ts";
import {storeToRefs} from "pinia";
import {toast} from "vue-sonner";
import router from "@/router/index.js";
import AppointmentList from "@/components/appointments/AppointmentList.vue";
import { useAppointments } from "@/composables/useAppointments.js";

const store = useDoctorAppointmentsStore();
const { dailyQueue } = storeToRefs(store);
const { stats, appointmentsByTab, calculateWaitTime } = useAppointments(dailyQueue);

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
            />
          </TabsContent>

        </Tabs>
      </CardContent>
    </Card>
</div>
</template>

<style scoped>

</style>
