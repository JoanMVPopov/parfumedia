<!-- src/views/HomePage.vue -->
<template>
  <div class="container mx-auto px-4 py-8">
    <div class="items-center flex flex-col text-center pt-[50px] lg:pt-[50px] mb-20">
      <h1 class="text-4xl sm:text-5xl sm:leading-none lg:text-7xl">
        <span class="block"> Explore the data </span>
        <span class="block text-primary font-medium"> Smell like the trend </span>
      </h1>
      <p class="max-w-md pt-2 my-3 text-sm sm:mt-5 lg:mb-0 sm:text-base lg:text-lg">
        Lorem ipsum dolor sit amet, consectetur adipiscing elit. Nam ultricies interdum libero, a rhoncus justo porta vitae. Aliquam faucibus id diam non aliquam.
      </p>
    </div>

    <div class="flex flex-wrap -mx-2">
      <PageCard
        v-for="(card, index) in cards"
        :key="index"
        :title="card.title"
        :description="card.description"
        :route="card.route"
      />
    </div>


    <div class="columns is-multiline">
      <div class="column is-12">
        <h2 class="is-size-2 has-text-centered">Latest Products</h2>
      </div>

      <div class="column is-3"
           v-for="product in latestProducts"
           v-bind:key="product.id">
        <div class="box"
        >
          <figure class="image mb-4">
            <img v-bind:src="product.get_thumbnail">
          </figure>

          <h3 class="is-size-4">{{product.name}}</h3>
          <p class="is-size-4">{{product.price}}</p>

          View details
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import PageCard from '../components/PageCard.vue';

import apiClient from "@/api";

export default {
  name: 'HomePage',
  mounted() {
    this.getLatestProducts()
  },
  methods: {
    getLatestProducts() {
      apiClient.get('/test/latest-products/')
          .then(response => {
            this.latestProducts = response.data
          }).catch(error => {
            console.log(error)
      })
    }
  },
  components: {
    PageCard,
  },
  data() {
    return {
      latestProducts: [],
      cards: [
        {
          title: 'ETL',
          description: 'See how data is Extracted, Transformed and Loaded',
          route: '/etl',
        },
        {
          title: 'EDA',
          description: 'Find out more about the dataset through Exploratory Data Analysis.',
          route: '/eda',
        },
        {
          title: 'Clusters',
          description: 'Explore clustering algorithms.',
          route: '/clusters',
        },
        {
          title: 'Classification',
          description: 'Understand classification methods.',
          route: '/classification',
        },
        {
          title: 'About',
          description: 'Learn more about this project.',
          route: '/about',
        },
          {
          title: 'About',
          description: 'Learn more about this project.',
          route: '/about',
        },
          {
          title: 'About',
          description: 'Learn more about this project.',
          route: '/about',
        },
          {
          title: 'About',
          description: 'Learn more about this project.',
          route: '/about',
        },
          {
          title: 'About',
          description: 'Learn more about this project.',
          route: '/about',
        },
          {
          title: 'About',
          description: 'Learn more about this project.',
          route: '/about',
        },
          {
          title: 'About',
          description: 'Learn more about this project.',
          route: '/about',
        },
      ],
    };
  },
};
</script>