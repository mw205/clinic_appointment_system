<script setup>
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'

defineProps({
  title: String,
  value: [String, Number],
  description: String,
  color: {
    type: String,
    default: 'text-primary',
  },
})
</script>

<template>
  <Card>
    <CardHeader>
      <CardTitle :class="color">{{ title }}</CardTitle>
      <CardDescription>{{ description }}</CardDescription>
    </CardHeader>
    <CardContent>
      <p class="text-3xl font-bold">{{ value }}</p>
    </CardContent>
  </Card>
</template>
