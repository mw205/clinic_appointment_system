<script setup>

import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { toast } from 'vue-sonner'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Textarea } from '@/components/ui/textarea'
import { Label } from '@/components/ui/label'
import { Switch } from '@/components/ui/switch'
import { Card, CardHeader, CardTitle, CardContent, CardFooter } from '@/components/ui/card'
import { Skeleton } from '@/components/ui/skeleton'
import PrescriptionItems from '@/components/consultation/PrescriptionItems.vue'
import RequestedTests from '@/components/consultation/RequestedTests.vue'

import { useConsultationStore } from '@/stores/consultation'

const route = useRoute()
const router = useRouter()
const store = useConsultationStore()

const form = ref({
    diagnosis: '',
    notes: '',
    prescription_items: [],
    requested_tests: [],
    is_completed: false
})
onMounted(async () => {
    await store.loadAppointment(route.params.appointmentId)
    if (store.consultation) {
        form.value = { ...store.consultation }
    }
})
async function handleSave() {
    try {
        await store.save({
            ...form.value,
            appointment: route.params.appointmentId
        })
        toast.success('consultation saved successfully!')
    } catch {
        toast.error('error saving consultation')
    }
}
</script>

<template>
    <div class="max-w-3xl mx-auto p-6 flex flex-col gap-6">
        <h1 class="text-2xl font-bold">Consultation Record</h1>

        <div v-if="store.loading" class="flex flex-col gap-4">
            <Skeleton class="h-10 w-full" />
            <Skeleton class="h-32 w-full" />
            <Skeleton class="h-24 w-full" />
        </div>

        <Card v-else>
            <CardHeader>
                <CardTitle>Appointment #{{ $route.params.appointmentId }}</CardTitle>
            </CardHeader>

            <CardContent class="flex flex-col gap-5">

                <div class="flex flex-col gap-1.5">
                    <Label for="diagnosis">Diagnosis</Label>
                    <Input id="diagnosis" v-model="form.diagnosis" placeholder="Enter diagnosis..." />
                </div>

                <div class="flex flex-col gap-1.5">
                    <Label for="notes">Clinical Notes</Label>
                    <Textarea id="notes" v-model="form.notes" placeholder="Enter clinical notes..." />
                </div>

                <PrescriptionItems v-model="form.prescription_items" />
                <RequestedTests v-model="form.requested_tests" />

                <div class="flex items-center gap-3">
                    <Switch id="completed" v-model:checked="form.is_completed" />
                    <Label for="completed">Mark consultation as completed</Label>
                </div>

            </CardContent>

            <CardFooter class="flex gap-3">
                <Button @click="handleSave" :disabled="store.loading">
                    {{ store.loading ? 'Saving...' : 'Save Consultation' }}
                </Button>
                <Button variant="outline" @click="router.back()">Cancel</Button>
            </CardFooter>
        </Card>
        <p v-if="store.error" class="text-destructive text-sm">{{ store.error }}</p>
    </div>
</template>