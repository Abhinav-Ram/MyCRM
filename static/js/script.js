document.addEventListener('DOMContentLoaded', function () {
    const form = document.getElementById('quotationForm');
    const productTable = document.getElementById('productTable');
    const addRowButton = document.getElementById('addRow');
    const taxRateInput = document.getElementById('taxRate');
    const subtotal = document.getElementById('subtotal');
    const tax = document.getElementById('tax');
    const overall = document.getElementById('overall');
    const submitButton = document.getElementById('generateQuotation');

    // Add event listener for adding rows
    addRowButton.addEventListener('click', addRow);

    // Event delegation for removing rows
    productTable.addEventListener('click', function (e) {
        if (e.target.classList.contains('removeRow')) {
            const row = e.target.closest('tr');
            removeHiddenFields(row); // Remove corresponding hidden fields
            row.remove();
            calculateTotal();
        }
    });

    // Function to remove corresponding hidden fields
    function removeHiddenFields(row) {
        const hiddenFields = row.querySelectorAll('input[type="hidden"]');
        hiddenFields.forEach(hiddenField => {
            hiddenField.remove();
        });
    }


    // Calculate and update totals
    form.addEventListener('input', calculateTotal);

    // Calculate and update totals
    function calculateTotal() {
        let subTotalValue = 0;
        const taxRate = parseFloat(taxRateInput.value) || 0;

        const rows = productTable.querySelectorAll('tbody tr');

        rows.forEach(function (row) {
            const quantity = parseFloat(row.querySelector('.quantity').value) || 0;
            const uom = row.querySelector('.uom').value;
            const rate = parseFloat(row.querySelector('.rate').value) || 0;
            const marginType = row.querySelector('.marginType').value;
            const marginAmount = parseFloat(row.querySelector('.marginAmount').value) || 0;
            let amount = quantity * rate;
            let totalAmount = amount;

            if (marginType == 'P') {
                //console.log('IF')
                const marginPercent = marginAmount / 100;
                const marginCost = amount * marginPercent;
                totalAmount += marginCost;
                //console.log('marginCost')
                //console.log(marginCost)
            } else {
                console.log('ELSE')
                totalAmount += marginAmount;

            }

            row.querySelector('.amount').textContent = amount.toFixed(2);
            row.querySelector('.totalAmount').textContent = totalAmount.toFixed(2);

            subTotalValue += totalAmount;
        });


        const taxValue = (subTotalValue * (taxRate / 100));
        const totalValue = subTotalValue + taxValue;

        subtotal.textContent = subTotalValue.toFixed(2);
        tax.textContent = taxValue.toFixed(2);
        overall.textContent = totalValue.toFixed(2);
    }

    // Function to add a new row
    function addRow() {
        const tbody = productTable.querySelector('tbody');
        const newRow = tbody.insertRow();
        newRow.innerHTML = `
        <td><input type="text" class="productName w-full px-4 py-2 border rounded" required></td>
        <td><input type="text" class="productDescription w-full px-4 py-2 border rounded" required></td>
        <td><input type="number" step="0.01" class="quantity w-full px-4 py-2 border rounded" required></td>
        <td><input type="text" class="uom w-full px-4 py-2 border rounded" required></td>
        <td><input type="number" step="0.01" class="rate w-full px-4 py-2 border rounded" required></td>
        <td><span class="amount px-4 py-2">0.00</span></td>
        <td><input type="text" class="marginType w-full px-4 py-2 border rounded" required></td>
        <td><input type="number" step="0.01" class="marginAmount w-full px-4 py-2 border rounded" required></td>
        <td><span class="totalAmount px-4 py-2">0.00</span></td>
        <td><button type="button" class="removeRow px-4 py-2 bg-red-500 text-white rounded">[X]</button></td>
        `;
        // Create hidden input fields for the new row
        const productNameInput = document.createElement('input');
        productNameInput.type = 'hidden';
        productNameInput.name = 'productName';
        productNameInput.classList = 'productNameInput hidden-fields';
        productNameInput.value = '';
        newRow.cells[0].appendChild(productNameInput);

        const productDescriptionInput = document.createElement('input');
        productDescriptionInput.type = 'hidden';
        productDescriptionInput.name = 'productDescription';
        productDescriptionInput.classList = 'productDescriptionInput hidden-fields';
        productDescriptionInput.value = '';
        newRow.cells[1].appendChild(productDescriptionInput);

        const quantityInput = document.createElement('input');
        quantityInput.type = 'hidden';
        quantityInput.name = 'quantity';
        quantityInput.classList = 'quantityInput hidden-fields';
        quantityInput.value = '';
        newRow.cells[2].appendChild(quantityInput);

        const uomInput = document.createElement('input');
        uomInput.type = 'hidden';
        uomInput.name = 'uom';
        uomInput.classList = 'uomInput hidden-fields';
        uomInput.value = '';
        newRow.cells[2].appendChild(uomInput);

        const rateInput = document.createElement('input');
        rateInput.type = 'hidden';
        rateInput.name = 'rate';
        rateInput.classList = 'rateInput hidden-fields';
        rateInput.value = '';
        newRow.cells[3].appendChild(rateInput);

        const amountInput = document.createElement('input');
        amountInput.type = 'hidden';
        amountInput.name = 'amount';
        amountInput.classList = 'amountInput hidden-fields';
        amountInput.value = '';
        newRow.cells[4].appendChild(amountInput);

        const marginTypeInput = document.createElement('input');
        marginTypeInput.type = 'hidden';
        marginTypeInput.name = 'marginType';
        marginTypeInput.classList = 'marginTypeInput hidden-fields';
        marginTypeInput.value = '';
        newRow.cells[4].appendChild(marginTypeInput);

        const marginAmountInput = document.createElement('input');
        marginAmountInput.type = 'hidden';
        marginAmountInput.name = 'marginAmount';
        marginAmountInput.classList = 'marginAmountInput hidden-fields';
        marginAmountInput.value = '';
        newRow.cells[4].appendChild(marginAmountInput);

        const totalInput = document.createElement('input');
        totalInput.type = 'hidden';
        totalInput.name = 'total';
        totalInput.classList = 'totalInput hidden-fields';
        totalInput.value = '';
        newRow.cells[4].appendChild(totalInput);
    }

    function updateHiddenInputs() {

        const productNameInput = document.createElement('input');
        productNameInput.type = 'hidden';
        productNameInput.name = 'productNameAll';
        productNameInput.value = '';
        form.appendChild(productNameInput);

        const productDescriptionInput = document.createElement('input');
        productDescriptionInput.type = 'hidden';
        productDescriptionInput.name = 'productDescriptionAll';
        productDescriptionInput.value = '';
        form.appendChild(productDescriptionInput);

        const quantityInput = document.createElement('input');
        quantityInput.type = 'hidden';
        quantityInput.name = 'quantityAll';
        quantityInput.value = '';
        form.appendChild(quantityInput);

        const uomInput = document.createElement('input');
        uomInput.type = 'hidden';
        uomInput.name = 'uomAll';
        uomInput.value = '';
        form.appendChild(uomInput);

        const rateInput = document.createElement('input');
        rateInput.type = 'hidden';
        rateInput.name = 'rateAll';
        rateInput.value = '';
        form.appendChild(rateInput);

        const amountInput = document.createElement('input');
        amountInput.type = 'hidden';
        amountInput.name = 'amountAll';
        amountInput.value = '';
        form.appendChild(amountInput);

        const marginTypeInput = document.createElement('input');
        marginTypeInput.type = 'hidden';
        marginTypeInput.name = 'marginTypeAll';
        marginTypeInput.value = '';
        form.appendChild(marginTypeInput);

        const marginAmountInput = document.createElement('input');
        marginAmountInput.type = 'hidden';
        marginAmountInput.name = 'marginAmountAll';
        marginAmountInput.value = '';
        form.appendChild(marginAmountInput);

        const totalInput = document.createElement('input');
        totalInput.type = 'hidden';
        totalInput.name = 'totalAll';
        totalInput.value = '';
        form.appendChild(totalInput);

        const tbody = productTable.querySelectorAll('.productTableBody');
        const rows = tbody[0].children.length
        var quantity = 0;
        var rate = 0;
        var amount = 0, marginAmount = 0, total = 0;
        for (i = 0; i < rows; i++) {
            productNameInput.value += tbody[0].children[i].children[0].children[0].value + ",";
            productDescriptionInput.value += tbody[0].children[i].children[1].children[0].value + ",";
            quantity = tbody[0].children[i].children[2].children[0].value
            quantityInput.value += quantity + ",";
            uomInput.value += tbody[0].children[i].children[3].children[0].value + ",";
            rate = tbody[0].children[i].children[4].children[0].value;
            rateInput.value += rate + ",";
            amount = parseFloat(quantity) * parseFloat(rate);
            amountInput.value += amount + ",";
            marginTypeInput.value += tbody[0].children[i].children[6].children[0].value + ",";
            marginAmount = tbody[0].children[i].children[7].children[0].value
            marginAmountInput.value += marginAmount + ",";
            total = amount + parseFloat(marginAmount);
            totalInput.value += total + ",";
        }


        console.log(productNameInput.value)
        console.log(productDescriptionInput.value)
        console.log(quantityInput.value)
        console.log(uomInput.value)
        console.log(rateInput.value)
        console.log(amountInput.value)
        console.log(marginTypeInput.value)
        console.log(marginAmountInput.value)
        console.log(totalInput.value)
    }

    submitButton.addEventListener('click', function () {
        updateHiddenInputs();

        form.submit();
    });

});
