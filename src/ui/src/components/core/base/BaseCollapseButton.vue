<template>
	<button
		role="button"
		class="BaseCollapseIcon"
		:class="{ 'BaseCollapseIcon--collapsed': isCollapsed }"
		@click="isCollapsed = !isCollapsed"
	>
		<i class="material-symbols-outlined">{{ icon }}</i>
	</button>
</template>

<script setup lang="ts">
import { computed, PropType } from "vue";

const props = defineProps({
	direction: {
		type: String as PropType<"left-right" | "top-bottom">,
		required: true,
	},
});

const isCollapsed = defineModel({ type: Boolean, required: true });

const icon = computed(() =>
	props.direction === "left-right" ? "chevron_left" : "keyboard_arrow_up",
);
</script>

<style scoped>
.BaseCollapseIcon {
	border: none;
	border-radius: 50%;
	padding: 4px;
	display: flex;
	align-items: center;
	justify-content: center;
	background-color: transparent;

	height: 32px;
	width: 32px;
	cursor: pointer;

	transition: all 0.3s ease-in-out;
	transform: rotate(0deg);

	border: 1px solid var(--separatorColor);
}
.BaseCollapseIcon:hover {
	background: var(--separatorColor);
}

.BaseCollapseIcon--collapsed {
	transform: rotate(180deg);
}
</style>
