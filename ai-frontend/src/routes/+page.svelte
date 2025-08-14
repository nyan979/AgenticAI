<script lang="ts">
	import { page } from '$app/state';
	import Button from '$lib/components/ui/button/button.svelte';
	import * as Card from '$lib/components/ui/card/index.js';
	import { Toggle } from '$lib/components/ui/toggle/index.js';
	import Spinner from '@lucide/svelte/icons/loader-circle';
	import { slide } from 'svelte/transition';

	let sources: { news: string; selected: boolean }[] = $state([
		{ news: 'Reddit', selected: true },
		{ news: 'The Straight Times', selected: false },
		{ news: 'Mothership SG', selected: false },
		{ news: 'The Straight Times', selected: false }
	]);

	let pageState: 'default' | 'retrieving' = $state('default');
	let data: { title: string; summary: string }[] = $state([]);
	async function fetchNews(): Promise<void> {
		pageState = 'retrieving';
		try {
			const response = await fetch('http://127.0.0.1:5000');
			if (response.status == 200) {
				data = await response.json();
			}
		} catch {
			pageState = 'default';
		}
		pageState = 'default';
	}
</script>

<main class="bg-background flex h-screen w-full justify-center">
	<Card.Card
		class="flex h-full w-4/5 min-w-[1280px] flex-col items-center justify-center border-none overflow-y-auto"
	>
		<Card.Header class="w-full">
			<Card.Title class="w-full text-center text-4xl">
				{#if pageState === 'retrieving'}
                    Retrieving news sources. Please be patient...
                {:else}
					Please select your sources
				{/if}</Card.Title
			>
		</Card.Header>
		<Card.Content>
			<div class="flex w-1/2 min-w-[620px] flex-wrap justify-center gap-4">
				{#each sources as source, i}
					<Toggle
						onclick={() => {
							sources[i].selected = !sources[i].selected;
						}}>{source.news}</Toggle
					>
				{/each}
			</div>
		</Card.Content>
		{#if pageState == 'retrieving'}
			<Button disabled><Spinner class="animate-spin" /> Retrieving...</Button>
		{:else}
			<Button onclick={async () => await fetchNews()}>Generate</Button>
		{/if}

		{#if data.length}
			<div class="" transition:slide>
				<Card.Title>Here are the news I've found</Card.Title>
				{#each data as news}
					<Card.Card>
						<Card.Header>
							<Card.Title>{news.title}</Card.Title>
							<Card.Description>{news.summary}</Card.Description>
						</Card.Header>
					</Card.Card>
				{/each}
			</div>
		{/if}
	</Card.Card>
</main>
