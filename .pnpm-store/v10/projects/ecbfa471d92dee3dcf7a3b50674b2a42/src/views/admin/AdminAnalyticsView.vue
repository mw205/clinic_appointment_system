<script setup>
import { onMounted } from 'vue'
import { Badge } from '@/components/ui/badge'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Skeleton } from '@/components/ui/skeleton'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import ExportCSVButton from '@/components/analytics/ExportCSVButton.vue'
import { useAnalyticsStore } from '@/stores/analytics'

const store = useAnalyticsStore()

onMounted(() => {
  if (!store.summary) store.loadAll()
})

const STATUS_CONFIG = {
  confirmed: { label: 'Confirmed', class: 'bg-blue-100 text-blue-700 border-blue-200' },
  completed: { label: 'Completed', class: 'bg-emerald-100 text-emerald-700 border-emerald-200' },
  requested: { label: 'Requested', class: 'bg-slate-100 text-slate-700 border-slate-200' },
  checked_in: { label: 'Checked In', class: 'bg-violet-100 text-violet-700 border-violet-200' },
  cancelled: { label: 'Cancelled', class: 'bg-orange-100 text-orange-700 border-orange-200' },
  no_show: { label: 'No Show', class: 'bg-red-100 text-red-700 border-red-200' },
}

function statusClass(status) {
  return STATUS_CONFIG[status]?.class ?? 'bg-gray-100 text-gray-700 border-gray-200'
}

function statusLabel(status) {
  return STATUS_CONFIG[status]?.label ?? status.replace('_', ' ')
}
</script>

<template>
  <div class="flex flex-col gap-6">
    <div class="flex items-start justify-between gap-4">
      <div class="space-y-1">
        <h1 class="text-2xl font-semibold text-gray-950">Analytics</h1>
        <p class="text-sm text-gray-600">Status mix, peak hours, and export tools.</p>
      </div>
      <div class="flex gap-2">
        <ExportCSVButton type="appointments" label="Export Appointments CSV" />
        <ExportCSVButton type="consultations" label="Export Consultations CSV" />
      </div>
    </div>

    <div v-if="store.loading" class="grid gap-6 lg:grid-cols-2">
      <Skeleton class="h-72 rounded-lg" />
      <Skeleton class="h-72 rounded-lg" />
    </div>

    <template v-else-if="store.summary">
      <Tabs default-value="status" class="flex flex-col gap-6">
        <TabsList class="w-fit">
          <TabsTrigger value="status">Status</TabsTrigger>
          <TabsTrigger value="hours">Peak Hours</TabsTrigger>
        </TabsList>

        <TabsContent value="status">
          <Card class="border-gray-200 shadow-sm">
            <CardHeader><CardTitle>Appointments by Status</CardTitle></CardHeader>
            <CardContent class="space-y-4">
              <div
                v-for="row in store.filterByStatus"
                :key="row.status"
                class="grid grid-cols-[140px_1fr_48px] items-center gap-4"
              >
                <Badge :class="statusClass(row.status)" class="justify-center">
                  {{ statusLabel(row.status) }}
                </Badge>
                <div class="h-2 overflow-hidden rounded-full bg-gray-100">
                  <div
                    class="h-full rounded-full bg-blue-600"
                    :style="{
                      width: `${
                        store.summary.total_appointments
                          ? (row.count / store.summary.total_appointments) * 100
                          : 0
                      }%`,
                    }"
                  />
                </div>
                <span class="text-right font-semibold text-gray-900">{{ row.count }}</span>
              </div>
              <p v-if="!store.filterByStatus.length" class="text-sm text-muted-foreground">
                No data for selected filter.
              </p>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="hours">
          <Card class="border-gray-200 shadow-sm">
            <CardHeader><CardTitle>Peak Appointment Hours</CardTitle></CardHeader>
            <CardContent class="space-y-3">
              <!-- FIX: was store.peakHours — field is store.summary.peak_hours -->
              <div
                v-for="entry in store.summary.peak_hours"
                :key="entry.hour"
                class="grid grid-cols-[72px_1fr_96px] items-center gap-4"
              >
                <span class="font-medium text-gray-700">
                  {{ String(entry.hour).padStart(2, '0') }}:00
                </span>
                <div class="h-2 overflow-hidden rounded-full bg-gray-100">
                  <div
                    class="h-full rounded-full bg-emerald-600"
                    :style="{
                      width: `${
                        store.summary.total_appointments
                          ? (entry.count / store.summary.total_appointments) * 100
                          : 0
                      }%`,
                    }"
                  />
                </div>
                <span class="text-right text-sm font-semibold text-gray-900">
                  {{ entry.count }}
                </span>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </template>
  </div>
</template>
