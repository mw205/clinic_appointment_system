<script setup>
import { onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { Badge } from '@/components/ui/badge'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Skeleton } from '@/components/ui/skeleton'
import { useConsultationStore } from '@/stores/consultation'

const route = useRoute()
const store = useConsultationStore()

onMounted(() => store.loadSummary(route.params.id))
</script>

<template>
  <div class="max-w-2xl mx-auto flex flex-col gap-6">
    <div class="flex items-center justify-between">
      <h1 class="text-2xl font-bold">Your Consultation Summary</h1>
      <Badge
        v-if="store.consultation"
        :class="
          store.consultation.is_completed
            ? 'bg-emerald-100 text-emerald-700 border-emerald-200'
            : 'bg-amber-100 text-amber-700 border-amber-200'
        "
      >
        {{ store.consultation.is_completed ? 'Completed' : 'In Progress' }}
      </Badge>
    </div>

    <div v-if="store.loading" class="flex flex-col gap-4">
      <Skeleton class="h-32 w-full" />
      <Skeleton class="h-24 w-full" />
    </div>

    <template v-else-if="store.consultation">
      <Card>
        <CardHeader><CardTitle>Diagnosis</CardTitle></CardHeader>
        <CardContent>
          <p class="text-sm leading-relaxed">{{ store.consultation.diagnosis }}</p>
        </CardContent>
      </Card>

      <Card v-if="store.consultation.prescription_items?.length">
        <CardHeader><CardTitle>Prescribed Medications</CardTitle></CardHeader>
        <CardContent>
          <ul class="flex flex-col gap-3">
            <li
              v-for="(item, i) in store.consultation.prescription_items"
              :key="i"
              class="flex flex-wrap items-center gap-2 p-2 rounded-md bg-blue-50 border border-blue-100"
            >
              <Badge class="bg-blue-100 text-blue-700 border-blue-200">{{ item.drug }}</Badge>
              <span class="text-sm text-muted-foreground">{{ item.dose }}</span>
              <span class="text-sm text-muted-foreground">· {{ item.duration }}</span>
              <span v-if="item.instructions" class="text-xs text-muted-foreground italic">
                ({{ item.instructions }})
              </span>
            </li>
          </ul>
        </CardContent>
      </Card>

      <Card v-if="store.consultation.requested_tests?.length">
        <CardHeader><CardTitle>Requested Tests</CardTitle></CardHeader>
        <CardContent>
          <ul class="flex flex-col gap-3">
            <li
              v-for="(test, i) in store.consultation.requested_tests"
              :key="i"
              class="flex flex-wrap items-center gap-2 p-2 rounded-md bg-violet-50 border border-violet-100"
            >
              <Badge class="bg-violet-100 text-violet-700 border-violet-200">{{
                test.test_name
              }}</Badge>
              <span v-if="test.notes" class="text-sm text-muted-foreground">{{ test.notes }}</span>
            </li>
          </ul>
        </CardContent>
      </Card>
    </template>

    <p v-else class="text-muted-foreground">No consultation record found.</p>
    <p v-if="store.error" class="text-destructive text-sm">{{ store.error }}</p>
  </div>
</template>
