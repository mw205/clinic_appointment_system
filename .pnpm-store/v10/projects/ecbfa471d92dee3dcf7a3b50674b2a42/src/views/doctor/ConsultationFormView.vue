<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { toast } from 'vue-sonner'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Textarea } from '@/components/ui/textarea'
import { Label } from '@/components/ui/label'
import { Badge } from '@/components/ui/badge'
import { Card, CardContent, CardFooter, CardHeader, CardTitle } from '@/components/ui/card'
import { Skeleton } from '@/components/ui/skeleton'
import PrescriptionItems from '@/components/consultation/PrescriptionItems.vue'
import RequestedTests from '@/components/consultation/RequestedTests.vue'
import { useConsultationStore } from '@/stores/consultation'

const route = useRoute()
const router = useRouter()
const store = useConsultationStore()
const markingComplete = ref(false)

const form = ref({
  diagnosis: '',
  notes: '',
  prescription_items: [],
  requested_tests: [],
})

onMounted(async () => {
  await store.loadForAppointment(route.params.appointmentId)
  if (store.consultation) {
    form.value = {
      diagnosis: store.consultation.diagnosis ?? '',
      notes: store.consultation.notes ?? '',
      prescription_items: store.consultation.prescription_items ?? [],
      requested_tests: store.consultation.requested_tests ?? [],
    }
  }
})

async function handleSave() {
  try {
    await store.save({
      ...form.value,
      appointment: route.params.appointmentId,
    })
    toast.success('Consultation saved successfully!')
  } catch {
    toast.error('Error saving consultation.')
  }
}

async function handleComplete() {
  if (!store.consultation?.id) {
    toast.error('Save the consultation first before completing it.')
    return
  }
  markingComplete.value = true
  try {
    await store.complete(store.consultation.id)
    toast.success('Consultation completed. Appointment marked as done.')
    router.back()
  } catch {
    toast.error('Failed to complete. Make sure the appointment is checked in.')
  } finally {
    markingComplete.value = false
  }
}
</script>

<template>
  <div class="max-w-3xl mx-auto flex flex-col gap-6">
    <div class="flex items-center justify-between">
      <h1 class="text-2xl font-bold">Consultation Record</h1>
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
      <Skeleton class="h-10 w-full" />
      <Skeleton class="h-32 w-full" />
      <Skeleton class="h-24 w-full" />
    </div>

    <Card v-else>
      <CardHeader>
        <CardTitle class="text-base text-muted-foreground">
          Appointment #{{ route.params.appointmentId }}
        </CardTitle>
      </CardHeader>

      <CardContent class="flex flex-col gap-5">
        <div class="flex flex-col gap-1.5">
          <Label for="diagnosis">Diagnosis</Label>
          <Input id="diagnosis" v-model="form.diagnosis" placeholder="Enter diagnosis..." />
        </div>

        <div class="flex flex-col gap-1.5">
          <Label for="notes">Clinical Notes</Label>
          <Textarea
            id="notes"
            v-model="form.notes"
            rows="4"
            placeholder="Enter clinical notes..."
          />
        </div>

        <PrescriptionItems v-model="form.prescription_items" />
        <RequestedTests v-model="form.requested_tests" />
      </CardContent>

      <CardFooter class="flex gap-3 flex-wrap">
        <Button @click="handleSave" :disabled="store.loading">
          {{ store.loading ? 'Saving...' : 'Save Consultation' }}
        </Button>

        <Button
          variant="secondary"
          :disabled="markingComplete || store.consultation?.is_completed"
          @click="handleComplete"
        >
          {{
            store.consultation?.is_completed
              ? '✓ Already Completed'
              : markingComplete
                ? 'Completing...'
                : 'Complete Consultation'
          }}
        </Button>

        <Button variant="outline" @click="router.back()">Cancel</Button>
      </CardFooter>
    </Card>

    <p v-if="store.error" class="text-destructive text-sm">{{ store.error }}</p>
  </div>
</template>
