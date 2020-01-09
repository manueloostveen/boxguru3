from django.shortcuts import render
from scripts import product_fit_logic as pfl
from django.views import View
from .forms import (ProductForm, BoxForm)
from .tables import SimpleBoxTable
from boxes.models import Box
from django_tables2 import RequestConfig


# Helper functions
def find_perfect_match(requested_amount, queryset, product):
    """
    Function that returns a queryset of boxes that fit the requested amount of products
    :param requested_amount: number of products
    :param queryset: a list of Box objects from the database
    :param product: product object that needs to fit in a box
    :return:
    """

    # initialize empty queryset with matching boxes
    list_of_ids = []

    # iterate over all boxes in queryset and append if match is made
    for box_object in queryset:
        # success_boxes.append(box_object)
        amount_in_box = product.max_in_box(box_object.width,
                                           box_object.length,
                                           box_object.height)[0][0]

        # create a queryset containing matching boxes
        if amount_in_box == requested_amount:
            list_of_ids.append(box_object.id)

    success_boxes = Box.objects.filter(id__in=list_of_ids)

    return success_boxes


# Views
class FindMatchingBoxView(View):
    template_name = 'calculate/find_matching_box.html'
    form_class = BoxForm
    queryset = Box.objects.all()

    def get(self, request):
        context = {}
        context['form'] = self.form_class
        context['queryset'] = self.queryset
        return render(request, self.template_name, context)


def calculate_view(request):
    template_name = "calculate/find_perfect_box.html"
    context = {}
    form = ProductForm()

    # if request.method == 'GET':
    #     context['form'] = form
    #     # TODO ordering table is a get method, this means that the stuff should be here when ordering
    #
    #     return render(request, template_name, context)

    if request.method == 'GET':
        form = ProductForm(request.GET or None)
        context['form'] = form

        if form.is_valid():
            # create RectangularProduct based on form
            form_product = pfl.RectangularProduct(form.cleaned_data['width'],
                                                  form.cleaned_data['length'],
                                                  form.cleaned_data['height'],
                                                  form.cleaned_data['no_tipping'],
                                                  form.cleaned_data['no_stacking'])

            # set amount of products that should fit in a box
            requested_amount = form.cleaned_data['amount_of_products_in_box']

            # retrieve list of all boxes from database
            queryset = Box.objects.all()

            # initialize success message
            context[
                'success_message'] = f"Sorry, we did not find a box that fits exactly {requested_amount} product(s)."

            # create list of matching boxes
            success_boxes = find_perfect_match(requested_amount, queryset, form_product)

            # create success message and success table
            if success_boxes:
                context['success_boxes'] = success_boxes
                success_table = SimpleBoxTable(success_boxes)
                RequestConfig(request).configure(success_table)
                context['success_table'] = success_table
                context['success_message'] = f"Hoorah, we found {len(success_boxes)} matching box(es)"

                return render(request, template_name, context)

            # look for matching boxes by incrementing requested amount
            elif not success_boxes:
                context['qup_message'] = "We could not find a matching box by incrementing the needed amount UP."
                context['alternative_boxes_qup'] = []
                context['alternative_boxes_qdown'] = []

                for new_amount in range(requested_amount + 1, requested_amount + 100):

                    alternative_boxes_qup = find_perfect_match(new_amount, queryset, form_product)

                    if alternative_boxes_qup:
                        alternative_boxes_qup_table = SimpleBoxTable(alternative_boxes_qup)
                        RequestConfig(request).configure(alternative_boxes_qup_table)

                        context['alternative_boxes_qup'] = alternative_boxes_qup
                        context['alternative_boxes_qup_table'] = alternative_boxes_qup_table
                        context['qup_message'] = f"By increasing the product quantity to {new_amount},\
                                 we found {len(alternative_boxes_qup)} fitting box(es)!"
                        break

                context["qdown_message"] = "We could not find a matching box by incrementing the needed amount DOWN."

                for new_amount in range(requested_amount - 1, 0, -1):

                    alternative_boxes_qdown = find_perfect_match(new_amount, queryset, form_product)

                    if alternative_boxes_qdown:
                        alternative_boxes_qdown_table = SimpleBoxTable(alternative_boxes_qdown)
                        RequestConfig(request).configure(alternative_boxes_qdown_table)

                        context['alternative_boxes_qdown'] = alternative_boxes_qdown
                        context['alternative_boxes_qdown_table'] = alternative_boxes_qdown_table
                        context['qdown_message'] = f"By decreasing the product quantity to {new_amount},\
                                 we found {len(alternative_boxes_qdown)} fitting box(es)!"
                        break

                return render(request, template_name, context)

        return render(request, template_name, context)


class CalculateView(View):
    template_name = 'calculate/find_perfect_box.html'
    context = {}

    def get(self, request):
        context = {}
        form = ProductForm()
        context['form'] = form
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        form = ProductForm(request.POST)
        self.context['form'] = form

        if form.is_valid():
            # create RectangularProduct based on form
            width = int(request.POST.get('width'))
            length = int(request.POST.get('length'))
            height = int(request.POST.get('height'))
            form_product = pfl.RectangularProduct(width,
                                                  length, height,
                                                  request.POST.get('no_tipping'),
                                                  request.POST.get('no_stacking'))

            # set amount of products that should fit in a box
            requested_amount = int(request.POST.get("amount_of_products_in_box"))

            # retrieve list of boxes from database
            queryset = Box.objects.all()

            # initialize succes message
            success_message = "Sorry, we could not find a matching box."

            # create list of matching boxes
            success_boxes = find_perfect_match(requested_amount, queryset, form_product)

            # initialize empty alternative box lists

            if success_boxes:
                success_message = f"Hoorah, we found {len(success_boxes)} matching box(es)"
                self.context['success_boxes'] = success_boxes
                self.context['success_message'] = success_message
                return render(request, self.template_name, self.context)

            # look for matching boxes by incrementing requested amount
            else:
                self.context["qup_message"] = "We could not find a matching box by incrementing the needed amount UP."

                for new_amount in range(requested_amount + 1, requested_amount + 100):
                    alternative_boxes_qup = find_perfect_match(new_amount, queryset, form_product)

                    if alternative_boxes_qup:
                        self.context["alternative_boxes_qup"] = alternative_boxes_qup
                        self.context["qup_message"] = f"By increasing the products to {new_amount},\
                         we found {len(alternative_boxes_qup)} fitting box(es)!"
                        break

                self.context[
                    "qdown_message"] = "We could not find a matching box by incrementing the needed amount DOWN."
                for new_amount in range(requested_amount - 1, 0, -1):
                    alternative_boxes_qdown = find_perfect_match(new_amount, queryset, form_product)
                    if alternative_boxes_qdown:
                        self.context["alternative_boxes_down"] = alternative_boxes_qdown
                        self.context["qdown_message"] = f"By decreasing the products to {new_amount},\
                         we found {len(alternative_boxes_qdown)} fitting box(es)!"
                        break

                # self.context.update({'form': form,
                #                      'success_message': success_message,
                #                      'success_boxes': success_boxes,
                #                      })

                print(self.context)

                return render(request, self.template_name, self.context)
