<script setup>
import {useDoctorAppointmentsStore} from "@/stores/DoctorAppointments.js";
import {onMounted, watch} from "vue";
import {Card, CardContent, CardDescription, CardHeader, CardTitle} from "@/components/ui/card/index.ts";
import {Button} from "@/components/ui/button/index.ts";
import {Tabs, TabsList, TabsTrigger, TabsContent} from "@/components/ui/tabs/index.ts";
import {Badge} from "@/components/ui/badge/index.ts";
import {Users, UserCheck} from "lucide-vue-next";
import {storeToRefs} from "pinia";
import {toast} from "vue-sonner";

const store = useDoctorAppointmentsStore();
const { actionStatus, actionMessage } = storeToRefs(store)



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

// watch(actionStatus, (status) => {
//   if (!status) return
//
//   if (status === 'success') {
//     toast.success(actionMessage.value)
//   } else if (status === 'error') {
//     toast.error(actionMessage.value)
//   }
//
//   actionStatus.value = null
//   actionMessage.value = ''
// })

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
            <TabsTrigger value="all">All ({{ store.dailyQueue.length }})</TabsTrigger>
            <TabsTrigger value="pending">Pending (0)</TabsTrigger>
<!--            <TabsTrigger value="checked-in">Checked In ({{ stats.checkedIn }})</TabsTrigger>-->
          </TabsList>

          <TabsContent value="all" class="space-y-3">
            <div
              v-for="apt in store.dailyQueue"
              :key="apt.id"
              class="p-4 rounded-lg border border-gray-200 hover:shadow-md transition-all"
            >
              <div class="flex items-start justify-between gap-4">
                <div class="flex items-start gap-4 flex-1">
                  <div class="p-2 bg-blue-100 rounded-lg">
                    <Users class="w-5 h-5 text-blue-600" />
                  </div>
                  <div class="flex-1">
                    <div class="flex items-center gap-3">
                      <p class="font-medium text-gray-900">{{ apt.patient.user.username }}</p>
                      <Badge  variant="secondary">
                        {{ apt.status }}
                      </Badge>
                      <Badge
                        variant="outline"
                        class="text-orange-600"
                      >
                        Waiting {{ 0 }} min
                      </Badge>
                    </div>
                    <div class="flex items-center gap-4 mt-2 text-sm text-gray-600">
                      <span class="flex items-center gap-1">
<!--                        <Clock class="w-4 h-4" />-->
                        {{ apt.startTime }} - {{ apt.endTime }}
                      </span>
<!--                      <span class="capitalize">{{ apt.type }}</span>-->
                    </div>
                  </div>
                </div>

<!--                actions -->
                <div class="flex gap-2 flex-shrink-0">

                  <Button
                    v-if="apt.status === 'confirmed'"
                    size="sm"
                    variant="outline"
                    @click="handleCheckIn(apt.id)"
                  >
                    <UserCheck class="w-4 h-4 mr-1" /> Check In
                  </Button>

                  <template v-if="apt.status === 'checked-in'">
                    <Button
                      size="sm"
                      class="bg-green-600 hover:bg-green-700"
                      @click="handleComplete(apt.id)"
                    >
                      Start Consultation
                    </Button>
                    <Button size="sm" variant="outline" @click="handleNoShow(apt.id)">
                      No Show
                    </Button>
                  </template>

                  <Button
                    v-if="apt.status === 'completed'"
                    size="sm"
                    variant="outline"
                    @click="handleNavigate('records')"
                  >
                    View Record
                  </Button>
                </div>
              </div>
            </div>
          </TabsContent>

<!--          <TabsContent value="pending">-->
<!--            <div-->
<!--              v-for="apt in queue.filter(a => a.status === 'pending')"-->
<!--              :key="apt.id"-->
<!--              class="p-4 rounded-lg border border-yellow-200 bg-yellow-50/50 mb-3"-->
<!--            >-->
<!--              <div class="flex items-start justify-between">-->
<!--                <div>-->
<!--                  <p class="font-medium text-gray-900">{{ apt.patientName }}</p>-->
<!--                  <p class="text-sm text-gray-600 mt-1">{{ apt.startTime }} - {{ apt.endTime }}</p>-->
<!--                </div>-->
<!--                <div class="flex gap-2">-->
<!--                  <Button size="sm" @click="handleConfirm(apt.id)">Confirm</Button>-->
<!--                  <Button size="sm" variant="outline" @click="handleDecline(apt.id)">Decline</Button>-->
<!--                </div>-->
<!--              </div>-->
<!--            </div>-->
<!--          </TabsContent>-->

<!--          <TabsContent value="checked-in">-->
<!--            <div-->
<!--              v-for="apt in queue.filter(a => a.status === 'checked-in')"-->
<!--              :key="apt.id"-->
<!--              class="p-4 rounded-lg border border-green-200 bg-green-50/50 mb-3"-->
<!--            >-->
<!--              <div class="flex items-start justify-between">-->
<!--                <div>-->
<!--                  <p class="font-medium text-gray-900">{{ apt.patientName }}</p>-->
<!--                  <p class="text-sm text-gray-600 mt-1">-->
<!--                    {{ apt.startTime }} - {{ apt.endTime }}-->
<!--                    <span v-if="apt.checkInTime"> &bull; Checked in at {{ apt.checkInTime }}</span>-->
<!--                  </p>-->
<!--                </div>-->
<!--                <Button size="sm" class="bg-green-600" @click="handleComplete(apt.id)">-->
<!--                  Start Consultation-->
<!--                </Button>-->
<!--              </div>-->
<!--            </div>-->
<!--          </TabsContent>-->
        </Tabs>
      </CardContent>
    </Card>
</div>
</template>

<style scoped>

</style>
