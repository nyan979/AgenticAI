<script lang="ts">
	import Button from '$lib/components/ui/button/button.svelte';
	import * as Card from '$lib/components/ui/card/index.js';
	import { Toggle } from '$lib/components/ui/toggle/index.js';
	import Square from '@lucide/svelte/icons/square';
	import Spinner from '@lucide/svelte/icons/loader-circle';
	import { fade, slide } from 'svelte/transition';
	import Input from '$lib/components/ui/input/input.svelte';

	let { email = $bindable() }: { email: string } = $props();

	let sources: { news: string; selected: boolean; img?: string }[] = $state([
		{ news: 'Reddit', selected: false, img: 'reddit.png' },
		{ news: 'The Strait Times', selected: false, img: 'strait-times.png' },
		{ news: 'Mothership', selected: false, img: 'mothership.png' },
		{ news: 'Channel News Asia', selected: false, img: 'cna.jpeg' }
	]);

	const DELAY_OFFSET: number = 0.5;
	let pageState: 'default' | 'retrieving' = $state('default');

	let isStopping: boolean = $state(false);
	let data: { title: string; summary: string; url: string }[] = $state([
		// {
		// 	title:
		// 		'I still feel guilty’: Man who tried to save pair in fatal Bukit Merah blaze wishes he could have done more - CNA',
		// 	summary:
		// 		'An emotional account from a man involved in a fatal fire at Bukit Merah who attempted to rescue victims and continues to struggle with feelings of guilt despite his heroic efforts.',
		// 	url: 'https://www.channelnewsasia.com/singapore/fire-bukit-merah-two-dead-hero-guilty-rescue-attempt-scdf-5294136'
		// }
	]);
	async function fetchNews(): Promise<void> {
		let source_rb = sources.filter((s) => s.selected).map((s) => s.news.toLowerCase());
		pageState = 'retrieving';
		let emails: string[] = [];
		if (email.trim().length) {
			emails.push(email);
		}
		
		try {
			const response = await fetch('http://127.0.0.1:5000/newsletter', {
				method: 'POST',
				headers: {
					'Content-Type': 'application/json'
				},
				body: JSON.stringify({
					sources: source_rb,
					emails
				})
			});
			if (response.status == 200) {
				if (!isStopping) {
					data = await response.json();
				}
				initialize();
			}
		} catch (e) {
			console.error(e);
			initialize();
		}
	}

	function initialize() {
		pageState = 'default';
		isStopping = false;
		sources = sources.map((s) => ({ img: s.img, selected: false, news: s.news }));
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
			<Card.Content class="flex flex-col justify-center items-center">
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
					<Input bind:value={email} placeholder="Email (optional)" class="mt-4 w-[22rem]" />
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
							sources = sources.map((s) => ({ img: s.img, selected: false, news: s.news }));
							pageState = 'default';
						}}><Square /></Button
					>
				{:else}
					<Button
						class="mt-4 w-[18rem] text-sm"
						disabled={sources.filter((s) => s.selected).length === 0}
						onclick={async () => await fetchNews()}>Generate</Button
					>
				{/if}
			</Card.Footer>
		{:else}
			<div class="flex h-3/4 w-full flex-col justify-center px-8" in:slide>
				<Card.Title class="sticky top-0 mb-4 text-3xl"
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
								<Card.Content
									class="text-muted-foreground flex w-full items-center gap-1 px-6 text-xs"
								>
									<span>Source:</span>
									<Button
										variant="link"
										class="flex w-0 grow justify-start truncate px-0 text-start"
										href={news.url}>{news.url}</Button
									></Card.Content
								>
							</Card.Card>
						</div>
					{/each}
				</div>

				<Button
					class="mt-4"
					onclick={() => {
						data = [];
						initialize();
					}}>Clear</Button
				>
			</div>
		{/if}
	</div>
</main>
