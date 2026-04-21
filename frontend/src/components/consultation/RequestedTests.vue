<script setup>
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';

const props = defineProps({
    modelValue: {
        type: Array,
        default: () => []
    }
});
const emit = defineEmits(['update:modelValue'])
function addItem() {
    emit('update:modelValue', [...props.modelValue, { name: '', notes: '' }]);
}

function removeItem(index) {
    emit('update:modelValue', props.modelValue.filter((item, i) => i !== index));
}

function updateItem(index, field, value) {
    const newItem = props.modelValue.map((item, i) =>
        i === index ? { ...item, [field]: value } : item
    )
    emit('update:modelValue', newItem)
}
</script>

<template>
    <div class="flex flex-col gap-3">
        <Label>Requested Tests</Label>
        <div v-for="(item, index) in modelValue" :key="index" class="flex gap-2 items-center">
            <Input placeholder="Test name" :value="item.name" @input="updateItem(index, 'name', $event.target.value)" />
            <Input placeholder="Notes (optional)" :value="item.notes"
                @input="updateItem(index, 'notes', $event.target.value)" />
            <Button variant="destructive" size="sm" @click="removeItem(index)">
                Remove
            </Button>
        </div>
        <Button variant="outline" size="sm" @click="addItem">
            Add Test ➕
        </Button>
    </div>
</template>