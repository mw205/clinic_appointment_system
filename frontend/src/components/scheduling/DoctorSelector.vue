<script setup>
import { computed, onMounted } from 'vue'
import { storeToRefs } from 'pinia'
import { useScheduleStore } from '@/stores/scheduling'
import Label from '@/components/ui/label/Label.vue'
import Select from '@/components/ui/select/Select.vue'
import SelectContent from '@/components/ui/select/SelectContent.vue'
import SelectItem from '@/components/ui/select/SelectItem.vue'
import SelectTrigger from '@/components/ui/select/SelectTrigger.vue'
import SelectValue from '@/components/ui/select/SelectValue.vue'

const props = defineProps({
  modelValue: {
    type: [Number, String],
    default: null,
  },
  placeholder: {
    type: String,
    default: 'Select a doctor',
  },
  label: {
    type: String,
    default: 'Doctor',
  },
  disabled: {
    type: Boolean,
    default: false,
  },
})

const emit = defineEmits(['update:modelValue'])

const store = useScheduleStore()
const { doctors, selectedDoctorId, loadingDoctors } = storeToRefs(store)

const selectedValue = computed({
  get() {
    const value = props.modelValue ?? selectedDoctorId.value
    return value != null ? String(value) : undefined
  },
  set(value) {
    const normalizedValue = value ? Number(value) : null
    selectedDoctorId.value = normalizedValue
    emit('update:modelValue', normalizedValue)
  },
})

const doctorLabel = (doctor) => {
  const fullName = [doctor.first_name, doctor.last_name].filter(Boolean).join(' ').trim()
  return fullName || doctor.username || doctor.email || `Doctor #${doctor.id}`
}

onMounted(async () => {
  if (!doctors.value.length && !loadingDoctors.value) {
    await store.loadDoctors()
  }
})
</script>

<template>
  <div class="space-y-2">
    <Label v-if="label">{{ label }}</Label>

    <Select v-model="selectedValue" :disabled="disabled || loadingDoctors">
      <SelectTrigger class="w-full">
        <SelectValue :placeholder="loadingDoctors ? 'Loading doctors...' : placeholder" />
      </SelectTrigger>

      <SelectContent>
        <SelectItem v-for="doctor in doctors" :key="doctor.id" :value="String(doctor.id)">
          {{ doctorLabel(doctor) }}
        </SelectItem>
      </SelectContent>
    </Select>

    <p v-if="!loadingDoctors && !doctors.length" class="text-sm text-muted-foreground">
      No doctors available.
    </p>
  </div>
</template>
