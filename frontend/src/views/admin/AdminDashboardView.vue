<script setup>
import ExportCSVButton from '@/components/analytics/ExportCSVButton.vue';
import { Badge } from '@/components/ui/badge';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Skeleton } from '@/components/ui/skeleton';
import { Table, TableBody, TableCell, TableEmpty, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { useAnalyticsStore } from '@/stores/analytics';
import { onMounted } from 'vue';


const store = useAnalyticsStore();

onMounted(() => store.loadAll());

function statusVariant(status) {
  const map = {
    confirmed: 'default',
    completed: 'secondary',
    cancelled: 'destructive',
    noshow: 'destructive',
    requested: 'outline',
    checked_in: 'secondary'
  }
  return map[status] ?? 'outline';
}
</script>

<template>
  <div class="p-6 flex flex-col gap-6">

    <div v-if="store.loading" class="grid grid-cols-2 md:grid-cols-4 gap-4">
      <Skeleton v-for="n in 4" :key="n" class="h-28 rounded-xl" />
    </div>

    <div v-else-if="store.summary" class="grid grid-cols-2 md:grid-cols-4 gap-4">
      <StatsCard title="Total Appointments" :value="store.summary.total" description="All time" />
      <StatsCard title="No-Show Rate" :value="store.summary.no_show_rate + '%'" description="Of all appointments" />
      <StatsCard title="Confirmed" :value="store.summary.by_status?.confirmed ?? 0" description="Currently confirmed" />
      <StatsCard title="Completed" :value="store.summary.by_status?.completed ?? 0" description="Fully completed" />
    </div>



    <Tabs default-value="appointments">
      <TabsList>
        <TabsTrigger value="appointments">Appointments</TabsTrigger>
        <TabsTrigger value="analytics">Analytics</TabsTrigger>
      </TabsList>

      <TabsContent value="appointments" class="flex flex-col gap-4">
        <div class="flex justify-end gap-2">
          <ExportCSVButton type="appointments" label="Export Appointments CSV" />
          <ExportCSVButton type="consultations" label="Export Consultations CSV" />
        </div>

        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>ID</TableHead>
              <TableHead>Patient</TableHead>
              <TableHead>Doctor</TableHead>
              <TableHead>Date</TableHead>
              <TableHead>Status</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            <TableRow v-for="Appointment in store.summary?.appointments ?? []" :key="Appointment.id">
              <TableCell>#{{ Appointment.id }}</TableCell>
              <TableCell>{{ Appointment.patient }}</TableCell>
              <TableCell>{{ Appointment.doctor }}</TableCell>
              <TableCell>{{ new Date(Appointment.start_time).toLocaleString() }}</TableCell>
              <TableCell>
                <Badge :variant="statusVariant(Appointment.status)">
                  {{ Appointment.status }}
                </Badge>
              </TableCell>
            </TableRow>
            <TableEmpty v-if="!store.summary?.appointments?.length">
              No appointments found.
            </TableEmpty>
          </TableBody>
        </Table>
      </TabsContent>

      <TabsContent value="analytics" class="flex flex-col gap-4">
        <Card>
          <CardHeader>
            <CardTitle>Appointments by Status</CardTitle>
          </CardHeader>
          <CardContent>
            <ul class="flex flex-col gap-2">
              <li v-for="(count, status) in store.summary?.by_status ?? {}" :key="status"
                class="flex items-center justify-between">
                <Badge :variant="statusVariant(status)">
                  {{ status }}
                </Badge>
                <span class="font-mono font-bold">{{ count }}</span>
              </li>
            </ul>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Peak Appointment Hours</CardTitle>
          </CardHeader>
          <CardContent>
            <ul class="flex flex-col gap-2">
              <li v-for="entry in store.peakHours ?? []" :key="entry.hour"
                class="flex items-center justify-between text-sm">
                <span>{{ String(entry.hour).padStart(2, '0') }}:00</span>
                <span class="font-mono font-bold">{{ entry.count }} appointments</span>
              </li>
            </ul>
          </CardContent>
        </Card>
      </TabsContent>
    </Tabs>
  </div>
</template>
