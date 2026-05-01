<script setup>
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'

const props = defineProps({
  modelValue: { type: Array, default: () => [] },
})
const emit = defineEmits(['update:modelValue'])

function addItem() {
  emit('update:modelValue', [
    ...props.modelValue,
    { drug: '', dose: '', duration: '', instructions: '' },
  ])
}

function removeItem(index) {
  emit(
    'update:modelValue',
    props.modelValue.filter((_, i) => i !== index),
  )
}

function updateItem(index, field, value) {
  const updated = props.modelValue.map((item, i) =>
    i === index ? { ...item, [field]: value } : item,
  )
  emit('update:modelValue', updated)
}
</script>

<template>
  <div class="flex flex-col gap-3">
    <Label>Prescription Items</Label>

    <div
      v-for="(item, index) in modelValue"
      :key="index"
      class="grid grid-cols-2 md:grid-cols-4 gap-2 p-3 rounded-lg border bg-muted/30"
    >
      <Input
        placeholder="Drug name"
        :value="item.drug"
        @input="updateItem(index, 'drug', $event.target.value)"
      />
      <Input
        placeholder="Dose"
        :value="item.dose"
        @input="updateItem(index, 'dose', $event.target.value)"
      />
      <Input
        placeholder="Frequency"
        :value="item.duration"
        @input="updateItem(index, 'duration', $event.target.value)"
      />
      <div class="flex gap-2">
        <Input
          placeholder="Instructions"
          :value="item.instructions"
          @input="updateItem(index, 'instructions', $event.target.value)"
        />
        <Button variant="destructive" size="sm" @click="removeItem(index)">✕</Button>
      </div>
    </div>

    <Button variant="outline" size="sm" class="w-fit" @click="addItem">
      Add Prescription ➕
    </Button>
  </div>
</template>
