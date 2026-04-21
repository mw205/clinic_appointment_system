<script setup>
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
const props = defineProps({
    modelValue: {
        type: Array,
        default: () => [] //So each componenet get a new array instead of sharing the same one
    }
});
const emit = defineEmits(['update:modelValue']);

function addItem() {
    emit('update:modelValue', [...props.modelValue, { name: '', dose: '', frequency: '' }]);
}
function removeItem(index) {
    emit('update:modelValue', props.modelValue.filter((item, i) => i !== index));
}
function updateItem(index) {
    const newItem = props.modelValue.map((item, i) =>
        i === index ? { ...item, [field]: value } : item
    )
    emit('update:modelValue', newItem);
}
</script>

<template>
    <div class="flex flex-col gap-3">
        <Label>Prescription Items</Label>

        <div v-for="(item, index) in modelValue" :key="index" class="flex gap-2 items-center">
            <Input placeholder="Medicine name" :value="item.name"
                @input="updateItem(index, 'name', $event.target.value)" />
            <Input placeholder="Dose" :value="item.dose" @input="updateItem(index, 'dose', $event.target.value)" />
            <Input placeholder="Frequency" :value="item.frequency"
                @input="updateItem(index, 'frequency', $event.target.value)" />
            <Button variant="destructive" size="sm" @click="removeItem(index)">
                Remove
            </Button>
        </div>
        <Button variant="outline" size="sm" @click="addItem">
            Add Prescription ➕
        </Button>
    </div>
</template>