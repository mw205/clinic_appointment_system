<script setup>
import { onMounted, ref, computed, watch } from 'vue'
import { Badge } from '@/components/ui/badge'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Skeleton } from '@/components/ui/skeleton'
import { Table, TableBody, TableCell, TableEmpty, TableHead, TableHeader, TableRow, } from '@/components/ui/table'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import ExportCSVButton from '@/components/analytics/ExportCSVButton.vue'
import StatsCard from '@/components/analytics/StatsCard.vue'
import { useAnalyticsStore } from '@/stores/analytics'
import * as appointmentService from '@/services/appointmentService.js'

const store = useAnalyticsStore()
const appointments = ref([])
const appointmentsLoading = ref(false)
const appointmentsError = ref(null)
const pagination = ref({
  count: 0,
  next: null,
  previous: null,
  currentPage: 1,
  totalPages: 1,
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

function statByKey(key) {
  return store.summary?.appointment_status_counts?.find((s) => s.status === key)?.count ?? 0
}

const appointmentStatusFilter = ref('')
const filteredAppointments = computed(() => {
  if (!appointmentStatusFilter.value) return appointments.value
  return appointments.value.filter((appointment) => appointment.status === appointmentStatusFilter.value)
})

function getPageFromUrl(url) {
  if (!url) return null
  try {
    const parsedUrl = new URL(url)
    const page = Number(parsedUrl.searchParams.get('page'))
    return Number.isFinite(page) && page > 0 ? page : null
  } catch {
    return null
  }
}

function updatePagination(data, requestedPage = 1) {
  const results = Array.isArray(data?.results) ? data.results : []
  const count = Number(data?.count ?? results.length)
  const previousPage = getPageFromUrl(data?.previous)
  const nextPage = getPageFromUrl(data?.next)
  const currentPage = Number(requestedPage) > 0
    ? Number(requestedPage)
    : previousPage
      ? previousPage + 1
      : nextPage
        ? nextPage - 1
        : 1

  const pageSize = results.length || 1
  const totalPages = Math.max(1, Math.ceil(count / pageSize))

  pagination.value = {
    count,
    next: data?.next ?? null,
    previous: data?.previous ?? null,
    currentPage,
    totalPages,
  }
}

const loadAppointments = async (params = {}) => {
  appointmentsLoading.value = true
  appointmentsError.value = null
  try {
    const data = await appointmentService.getAppointments({ page: 1, ...params })
    appointments.value = data?.results ?? data ?? []
    updatePagination(data, params.page ?? 1)
  } catch (error) {
    appointmentsError.value = 'Could not load appointments.'
  } finally {
    appointmentsLoading.value = false
  }
}

const changePage = (page) => {
  const status = appointmentStatusFilter.value
  loadAppointments({ page, ...(status ? { status } : {}) })
}

watch(appointmentStatusFilter, (status) => {
  const params = status ? { status, page: 1 } : { page: 1 }
  loadAppointments(params)
})

onMounted(() => {
  store.loadAll()
  loadAppointments()
})
</script>

<template>
  <div class="flex flex-col gap-6">
    <h1 class="text-2xl font-semibold text-gray-900">Admin Dashboard</h1>

    <div v-if="store.loading" class="grid grid-cols-2 md:grid-cols-4 gap-4">
      <Skeleton v-for="n in 4" :key="n" class="h-28 rounded-xl" />
    </div>

    <div v-else-if="store.summary" class="grid grid-cols-2 md:grid-cols-4 gap-4">
      <StatsCard
        title="Total Appointments"
        :value="store.summary.total_appointments ?? 0"
        description="All time"
        color="text-blue-600"
      />
      <StatsCard
        title="No-Show Rate"
        :value="(store.summary.no_show_rate ?? 0) + '%'"
        description="Of all appointments"
        color="text-red-600"
      />
      <StatsCard
        title="Confirmed"
        :value="statByKey('confirmed')"
        description="Currently confirmed"
        color="text-blue-500"
      />
      <StatsCard
        title="Completed"
        :value="statByKey('completed')"
        description="Fully completed"
        color="text-emerald-600"
      />
    </div>

    <Tabs default-value="appointments">
      <TabsList>
        <TabsTrigger value="appointments">Appointments</TabsTrigger>
        <TabsTrigger value="analytics">Analytics</TabsTrigger>
      </TabsList>

      <TabsContent value="appointments" class="flex flex-col gap-4 mt-4">
        <div class="flex flex-wrap items-center justify-between gap-3">
          <div class="flex items-center gap-3">
            <label class="text-sm font-medium">Filter by status</label>
            <select
              v-model="appointmentStatusFilter"
              class="h-9 rounded-md border border-input bg-background px-3 text-sm"
            >
              <option value="">All statuses</option>
              <option v-for="(cfg, key) in STATUS_CONFIG" :key="key" :value="key">
                {{ cfg.label }}
              </option>
            </select>
          </div>
          <div class="flex gap-2">
            <ExportCSVButton type="appointments" label="Export Appointments CSV" />
            <ExportCSVButton type="consultations" label="Export Consultations CSV" />
          </div>
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
            <TableRow
              v-for="appointment in filteredAppointments"
              :key="appointment.id"
            >
              <TableCell>#{{ appointment.id }}</TableCell>
              <TableCell>{{ appointment.patient?.name ?? '—' }}</TableCell>
              <TableCell>{{ appointment.doctor?.name ?? '—' }}</TableCell>
              <TableCell>{{ new Date(appointment.start_time).toLocaleString() }}</TableCell>
              <TableCell>
                <Badge :class="statusClass(appointment.status)">
                  {{ statusLabel(appointment.status) }}
                </Badge>
              </TableCell>
            </TableRow>
            <TableEmpty v-if="!appointmentsLoading && !filteredAppointments.length">
              No appointments found.
            </TableEmpty>
          </TableBody>
        </Table>
        <div class="flex items-center justify-between text-sm text-gray-600">
          <span>Showing {{ filteredAppointments.length }} of {{ pagination.count }}</span>
          <div class="flex items-center gap-2">
            <button
              class="h-9 rounded-md border px-3"
              :disabled="pagination.currentPage <= 1 || appointmentsLoading"
              @click="changePage(pagination.currentPage - 1)"
            >
              Previous
            </button>
            <span>Page {{ pagination.currentPage }} of {{ pagination.totalPages }}</span>
            <button
              class="h-9 rounded-md border px-3"
              :disabled="pagination.currentPage >= pagination.totalPages || appointmentsLoading"
              @click="changePage(pagination.currentPage + 1)"
            >
              Next
            </button>
          </div>
        </div>
        <p v-if="appointmentsError" class="text-destructive text-sm">{{ appointmentsError }}</p>
      </TabsContent>

      <TabsContent value="analytics" class="flex flex-col gap-4 mt-4">
        <div class="flex items-center gap-3">
          <label class="text-sm font-medium">Filter by status</label>
          <select
            v-model="store.filter"
            class="h-9 rounded-md border border-input bg-background px-3 text-sm"
          >
            <option value="">All statuses</option>
            <option v-for="(cfg, key) in STATUS_CONFIG" :key="key" :value="key">
              {{ cfg.label }}
            </option>
          </select>
        </div>

        <Card>
          <CardHeader><CardTitle>Appointments by Status</CardTitle></CardHeader>
          <CardContent>
            <ul class="flex flex-col gap-2">
              <li
                v-for="entry in store.filterByStatus"
                :key="entry.status"
                class="flex items-center justify-between p-2 rounded-md"
              >
                <Badge :class="statusClass(entry.status)">
                  {{ statusLabel(entry.status) }}
                </Badge>
                <span class="font-mono font-bold text-sm">{{ entry.count }}</span>
              </li>
              <li v-if="!store.filterByStatus.length" class="text-sm text-muted-foreground">
                No data for selected filter.
              </li>
            </ul>
          </CardContent>
        </Card>

        <Card>
          <CardHeader><CardTitle>Peak Appointment Hours</CardTitle></CardHeader>
          <CardContent>
            <ul class="flex flex-col gap-2">
              <li
                v-for="entry in store.summary?.peak_hours ?? []"
                :key="entry.hour"
                class="flex items-center justify-between text-sm p-2 rounded-md hover:bg-muted/50"
              >
                <span class="font-medium w-16"> {{ String(entry.hour).padStart(2, '0') }}:00 </span>
                <div class="flex-1 mx-4 h-2 rounded-full bg-muted overflow-hidden">
                  <div
                    class="h-full rounded-full bg-blue-400"
                    :style="{ width: `${Math.min(entry.count * 8, 100)}%` }"
                  />
                </div>
                <span class="font-mono font-bold w-6 text-right">{{ entry.count }}</span>
              </li>
            </ul>
          </CardContent>
        </Card>
      </TabsContent>
    </Tabs>

    <p v-if="store.error" class="text-destructive text-sm">{{ store.error }}</p>
  </div>
</template>
