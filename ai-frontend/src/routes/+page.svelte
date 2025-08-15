<script lang="ts">
	import Button from '$lib/components/ui/button/button.svelte';
	import * as Card from '$lib/components/ui/card/index.js';
	import { Toggle } from '$lib/components/ui/toggle/index.js';
	import Square from '@lucide/svelte/icons/square';
	import Spinner from '@lucide/svelte/icons/loader-circle';
	import { fade, slide } from 'svelte/transition';

	let sources: { news: string; selected: boolean; img?: string }[] = $state([
		{ news: 'Reddit', selected: false, img: 'reddit.png' },
		{ news: 'The Strait Times', selected: false, img: 'strait-times.png' },
		{ news: 'Mothership', selected: false, img: 'mothership.png' },
		{ news: 'Yahoo News', selected: false, img: 'yahoo.png' },
		{ news: 'Channel News Asia', selected: false, img: 'cna.jpeg' }
	]);

	const DELAY_OFFSET: number = 0.5;
	let pageState: 'default' | 'retrieving' = $state('default');

	let emails: string[] = $state([]);
	let isStopping: boolean = $state(false);
	let data: { title: string; summary: string; source: string }[] = $state([]);
	async function fetchNews(): Promise<void> {
		let source_rb = sources.filter((s) => s.selected).map((s) => s.news.toLowerCase());
		pageState = 'retrieving';
		try {
			const response = await fetch('http://127.0.0.1:5000/newsletter', {
				method: 'POST',
				headers: {
					'Content-Type': 'application/json'
				},
				body: JSON.stringify({
					sources: source_rb,
					emails: ['jarylozh@gmail.com']
				})
			});
			if (response.status == 200) {
				if (!isStopping) {
					data = await response.json();
					console.log(data);
				}
				pageState = 'default';
				isStopping = false;
			}
		} catch (e) {
			console.error(e);
			pageState = 'default';
			isStopping = false;
		}
	}
</script>

<main class="flex h-screen w-full justify-center">
	<div
		class="flex h-full w-1/2 min-w-[640px] flex-col items-center justify-center gap-4 overflow-y-auto border-none"
	>
		{#if !data.length}
			<Card.Header class="w-full">
				<Card.Title class="w-full text-center text-6xl">
					{#if pageState === 'retrieving'}
						<h1 class="text-2xl">Retrieving news sources. Please be patient...</h1>
					{:else}
						<h1>Generate Your Daily Brief</h1>
						<description class="text-muted-foreground text-base font-normal">
							Select your preferred sources to build and receive your custom news summary.
						</description>
					{/if}</Card.Title
				>
			</Card.Header>
			<Card.Content class="">
				{#if pageState == 'default'}
					<div class="flex w-1/2 min-w-[620px] flex-wrap justify-center gap-4">
						{#each sources as source, i}
							<Toggle
								onclick={() => {
									sources[i].selected = !sources[i].selected;
								}}
							>
								{#if sources[i].img}
									<img width="24" height="24" alt="" src={`/icons/${sources[i].img}`} />
								{/if}
								{source.news}</Toggle
							>
						{/each}
					</div>
				{/if}
			</Card.Content>

			<Card.Footer>
				{#if pageState == 'retrieving'}
					<Button disabled><Spinner class="animate-spin" /> Retrieving...</Button>
					<Button
						variant="secondary"
						class="ml-2"
						onclick={() => {
							isStopping = true;
							data = [];
							sources = sources.map(s => ({img: s.img, selected: false, news: s.news}))
							pageState = "default"
						}}><Square /></Button
					>
				{:else}
					<Button
						class="text-sm"
						disabled={sources.filter((s) => s.selected).length === 0}
						onclick={async () => await fetchNews()}>Generate</Button
					>
				{/if}
			</Card.Footer>
		{:else}
			<div class="flex h-3/4 w-full flex-col justify-center px-8" in:slide>
				<Card.Title class="sticky top-0 text-3xl mb-4"
					>Here are the top headlines for Singapore.</Card.Title
				>
				<div class="flex max-h-full flex-col gap-4 overflow-y-auto py-4">
					{#each data as news, i}
						<div transition:fade|local={{ delay: i * DELAY_OFFSET }}>
							<Card.Card>
								<Card.Header>
									<Card.Title>{news.title}</Card.Title>
									<Card.Description>{news.summary}</Card.Description>
								</Card.Header>
								<Card.Content class="text-muted-foreground text-xs"
									>Source: {news.source}</Card.Content
								>
							</Card.Card>
						</div>
					{/each}
				</div>

				<Button
					class="mt-4"
					onclick={() => {
						data = [];
						
					}}>Clear</Button
				>
			</div>
		{/if}
	</div>
</main>
