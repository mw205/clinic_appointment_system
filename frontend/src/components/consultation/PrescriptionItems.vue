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
        :model-value="item.drug"
        @update:model-value="(value) => updateItem(index, 'drug', value)"
      />
      <Input
        placeholder="Dose"
        :model-value="item.dose"
        @update:model-value="(value) => updateItem(index, 'dose', value)"
      />
      <Input
        placeholder="Frequency"
        :model-value="item.duration"
        @update:model-value="(value) => updateItem(index, 'duration', value)"
      />
      <div class="flex gap-2">
        <Input
          placeholder="Instructions"
          :model-value="item.instructions"
          @update:model-value="(value) => updateItem(index, 'instructions', value)"
        />
        <Button type="button" variant="destructive" size="sm" @click="removeItem(index)">x</Button>
      </div>
    </div>

    <Button type="button" variant="outline" size="sm" class="w-fit" @click="addItem">
      Add Prescription +
    </Button>
  </div>
</template>
