<template>
	<div v-if="ssbm.isSelectionActive()" class="BuilderSettingsHandlers">
		<div class="sectionTitle">
			<i class="material-symbols-outlined">bolt</i>
			<h3>Events</h3>
		</div>
		<div class="list">
			<div
				v-for="(eventInfo, eventType) in recognisedEvents"
				:key="eventType"
				class="fieldWrapper"
			>
				<div class="columns">
					<div class="fieldWrapperMain">
						<span class="name">{{ eventType }}</span>
						<div class="content">
							<BuilderSelect
								:model-value="
									component.handlers?.[eventType] ?? ''
								"
								:options="getOptions(eventType)"
								variant="embedded"
								enable-search
								@update:model-value="
									handleHandlerChange($event, eventType)
								"
							/>
						</div>
					</div>
					<div class="fieldActions">
						<button
							v-if="getStubCode(eventType)"
							variant="subtle"
							title="Show event handler stub"
							@click="showStub(eventType)"
						>
							<i class="material-symbols-outlined">help</i>
						</button>
					</div>
				</div>
				<div v-if="eventInfo?.desc" class="desc">
					{{ eventInfo.desc }}
				</div>
			</div>
		</div>
		<BuilderModal
			v-if="stubModal"
			:close-action="stubCloseAction"
			icon="help"
			:modal-title="stubModal?.modalTitle"
		>
			<div class="stubMessage">
				You can use the following stub code as a starting point for your
				event handler.
			</div>
			<div class="codeContainer">
				<code v-dompurify-html="stubModal.highlightedCodeHtml"> </code>
			</div>
			<button @click="copyToClipboard(stubModal.code)">
				<i class="material-symbols-outlined"> content_copy </i>
				Copy code to clipboard
			</button>
		</BuilderModal>
		<div class="customHandler">
			<button
				title="Add a custom event handler"
				@click="showCustomHandlerModal"
			>
				<i class="material-symbols-outlined">add</i>Add custom handler
			</button>
			<BuilderModal
				v-if="customHandlerModal"
				:close-action="customHandlerModalCloseAction"
				icon="bolt"
				modal-title="Add Custom Event Handler"
			>
				<div class="customHandlerModalForm">
					<div class="fieldWrapper">
						<div class="fieldWrapperMain">
							<span class="name">Event type</span>
							<input
								v-model="customHandlerModal.eventType"
								class="content"
								type="text"
								list="commonEventTypes"
							/>
							<datalist id="commonEventTypes">
								<option
									v-for="commonEventType in commonEventTypes"
									:key="commonEventType"
									:value="commonEventType"
								>
									{{ commonEventType }}
								</option>
							</datalist>
						</div>
						<span class="desc">Can be any event type.</span>
					</div>
					<div class="fieldWrapper">
						<div class="fieldWrapperMain">
							<span class="name">Handler function</span>
						</div>
						<select
							v-model="customHandlerModal.handlerFunctionName"
							class="content"
						>
							<option
								v-for="userFunction in userFunctions"
								:key="userFunction.name"
								:value="userFunction.name"
							>
								{{ userFunction.name }}
							</option>
							<option
								v-for="pageKey in pageKeys"
								:key="`$goToPage_${pageKey}`"
								:value="`$goToPage_${pageKey}`"
							>
								Go to page "{{ pageKey }}"
							</option>
							<option
								v-for="workflowKey in workflowKeys"
								:key="`$runWorkflow_${workflowKey}`"
								:value="`$runWorkflow_${workflowKey}`"
							>
								Run workflow "{{ workflowKey }}"
							</option>
						</select>
						<span class="desc"
							>The function that will handle the event.</span
						>
					</div>
				</div>

				<button @click="addCustomEventHandler()">
					<i class="material-symbols-outlined">add</i>Add
				</button>
			</BuilderModal>
		</div>
	</div>
</template>

<script setup lang="ts">
import * as monaco from "monaco-editor";

import { computed, ComputedRef, inject, Ref, ref } from "vue";
import { useComponentActions } from "../useComponentActions";
import injectionKeys from "@/injectionKeys";
import BuilderModal, { ModalAction } from "../BuilderModal.vue";
import { WriterComponentDefinition } from "@/writerTypes";
import BuilderSelect from "../BuilderSelect.vue";
import type { Option } from "../BuilderSelect.vue";

const wf = inject(injectionKeys.core);
const ssbm = inject(injectionKeys.builderManager);

const { setHandlerValue } = useComponentActions(wf, ssbm);
const component = computed(() => wf.getComponentById(ssbm.getSelectedId()));

const options = computed<Option[]>(() => {
	const userFunctionsOptions: Option[] = userFunctions.value
		.map((v) => v.name)
		.map((v) => ({ value: v, label: v, icon: "function" }));

	const pageKeyOptions: Option[] = pageKeys.value.map((v) => ({
		label: `Go to page "${v}"`,
		value: `$goToPage_${v}`,
		icon: "link",
	}));

	const workflowKeyOptions: Option[] = workflowKeys.value.map((v) => ({
		label: `Run workflow "${v}"`,
		value: `$runWorkflow_${v}`,
		icon: "linked_services",
	}));

	return [
		{ label: "(No handler)", value: "", icon: "block" },
		...userFunctionsOptions,
		...pageKeyOptions,
		...workflowKeyOptions,
	];
});

function getOptions(eventType: string): Option[] {
	if (!isHandlerInvalid(eventType)) return options.value;

	const handler = component.value.handlers?.[eventType];

	return [
		...options.value,
		{ value: handler, label: `${handler} (Not found)` },
	];
}

const recognisedEvents: ComputedRef<WriterComponentDefinition["events"]> =
	computed(() => {
		const { type } = component.value;
		const { events: supportedEvents } = wf.getComponentDefinition(type);

		const recEvents = { ...supportedEvents };

		Object.keys({ ...component.value.handlers }).forEach((eventType) => {
			if (recEvents[eventType]) return;
			recEvents[eventType] = { desc: "Custom event" };
		});

		return recEvents;
	});

const userFunctions = wf.userFunctions;

const pageKeys = computed(() => {
	const pages = wf.getComponents("root");
	const pageKeys = pages
		.filter((page) => page.type == "page")
		.map((page) => page.content["key"])
		.filter((pageKey) => Boolean(pageKey));
	return pageKeys;
});

const workflowKeys = computed(() => {
	const workflows = wf.getComponents("workflows_root");
	const workflowKeys = workflows
		.filter((workflow) => workflow.type == "workflows_workflow")
		.map((workflow) => workflow.content["key"])
		.filter((workflowKey) => Boolean(workflowKey));
	return workflowKeys;
});

const isHandlerInvalid = (eventType: string) => {
	const handlerFunctionName = component.value.handlers?.[eventType];
	if (!handlerFunctionName) return false;

	// $ is reserved for frontend internal use, such as page change

	if (handlerFunctionName.startsWith("$")) {
		return false;
	}
	if (userFunctions.value.some((uf) => uf.name == handlerFunctionName))
		return false;
	return true;
};

const handleHandlerChange = (functionName: string, eventType: string) => {
	setHandlerValue(component.value.id, eventType, functionName);
};

type StubModal = {
	code: string;
	highlightedCodeHtml: string;
	modalTitle: string;
};

type CustomHandlerModal = {
	eventType: string;
	handlerFunctionName: string;
};

const stubModal: Ref<StubModal> = ref(null);
const customHandlerModal: Ref<CustomHandlerModal> = ref(null);

function getCustomEventStubCode() {
	return `
# When dealing with a DOM event, Writer Framework generates a payload by serialising its
# primitive properties (non-Object, non-function properties).

# If the event is instead an instance of CustomEvent,
# it looks for a "payload" property inside the CustomEvent's "detail" property. 

def handle_keydown(state, payload):
	print(payload) # Shows all the properties captured

	key_activated = payload.get("key")
	if key_activated == "ArrowLeft":
		state["position"] += -10
	elif key_activated == "ArrowRight":
		state["position"] += 10

	`;
}

function getStubCode(eventType: string) {
	const { type } = component.value;
	const { events } = wf.getComponentDefinition(type);
	const event = events?.[eventType];

	if (!event) return getCustomEventStubCode();

	return event?.stub;
}

async function showStub(eventType: string) {
	const code = getStubCode(eventType);
	const highlightedCodeHtml = await monaco.editor.colorize(
		code.trim(),
		"python",
		{},
	);
	stubModal.value = {
		modalTitle: `"${eventType}" event`,
		code,
		highlightedCodeHtml,
	};
}

const commonEventTypes = [
	"click",
	"mousedown",
	"mouseup",
	"mouseenter",
	"mouseleave",
	"mousemove",
	"keydown",
	"keyup",
	"keypress",
	"input",
	"change",
	"submit",
	"focus",
	"blur",
	"resize",
	"scroll",
	"load",
];

function addCustomEventHandler() {
	const { eventType, handlerFunctionName } = customHandlerModal.value;
	setHandlerValue(component.value.id, eventType, handlerFunctionName);
	customHandlerModal.value = null;
}

const stubCloseAction: ModalAction = {
	desc: "Close",
	fn: () => {
		stubModal.value = null;
	},
};

function showCustomHandlerModal() {
	customHandlerModal.value = {
		eventType: null,
		handlerFunctionName: null,
	};
}

const customHandlerModalCloseAction: ModalAction = {
	desc: "Close",
	fn: () => {
		customHandlerModal.value = null;
	},
};

const copyToClipboard = (text: string) => {
	navigator.clipboard.writeText(text);
};
</script>

<style scoped>
@import "../sharedStyles.css";

.list {
	border-radius: 4px;
}

.fieldWrapper .columns {
	display: grid;
	grid-template-columns: minmax(0, 100%) auto;
	gap: 12px;
	align-items: center;
	max-width: 100%;
}

.fieldWrapperMain {
	width: 100%;
}

.fieldWrapper .content {
	padding: 16px 8px 12px 8px;
	width: 100%;
}
.fieldWrapper .content .select {
	padding: 0;
	height: auto;
}

.fieldActions > button {
	border-radius: 16px;
	font-size: 0.875rem;
}

.customHandler {
	margin-top: 24px;
}

.addHandler .fields {
	display: flex;
	gap: 16px;
	margin-bottom: 16px;
}

.stubMessage {
	font-size: 0.8rem;
}

.codeContainer {
	white-space: pre-wrap;
	background: var(--builderSubtleHighlightColorSolid);
	padding: 16px;
	border-radius: 4px;
	font-family: Consolas, monospace;
	font-size: 0.85rem;
	margin-top: 12px;
	margin-bottom: 12px;
	overflow: hidden;
	text-overflow: ellipsis;
}

.codeContainer code {
	white-space: pre-wrap;
}

.customHandlerModalForm {
	display: flex;
	align-items: center;
	gap: 16px;
	margin-bottom: 16px;
}

.customHandlerModalForm .fieldWrapper {
	flex: 1 1 auto;
	margin-top: 0;
}
</style>
